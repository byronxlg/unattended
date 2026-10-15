# Fleet Audit

Python 3.12, with PyYAML 6.0.2. From this directory:

```sh
uv sync --locked
uv run fleet-audit --help
uv run fleet-audit declared /absolute/runbook/directory
uv run fleet-audit declared /absolute/runbook/directory --json
uv run python -m fleet_audit.acceptance registry --offline
uv run --with pytest pytest -q
```

`declared` recursively validates version 1 Markdown frontmatter, reads the declared
plists, and checks their labels. It returns 0 for a nonempty valid registry and 3
for invalid input. JSON includes validation errors; errors also go to stderr.
Paths and complete argument arrays are literal. `declared` opens no executable, working directory,
output, or receipt. Environment observations contain keys only.

A declared line proves only the registry and plist join.
It does not establish whether a service is loaded or doing useful work.

Fixtures are adjacent to the installed editable package in this checkout.
Acceptance uses injected fixture storage and never opens an original host path.
Synthetic runbooks use `/fleet-fixtures/` logical plist paths. For a console demo,
copy them into a temporary directory and replace `/fleet-fixtures/` with the
absolute directory containing copies of the fixture plists. Tests do this preparation
explicitly; the CLI never rewrites paths.
See `fixtures/README.md` for provenance and limitations.

Measured on the implementation host: package venv 1.0 MiB before temporary
console-demo fixtures; installed PyYAML files total 849,283 bytes (including
metadata and bytecode). The venv did not exist before installation. The shared uv
cache measured 2.0 GiB both before and after at `du -sh` resolution; a precise
cache delta was not recorded. Free space remained 2.6 GiB.
The backend is build-only, pinned to setuptools 75.8.0 in build-system and a
non-default `build` dependency group so its distribution is included in uv.lock.

## Observer and snapshot workflow

Increment 2 adds `uv run python -m fleet_audit.acceptance observer --offline`.
It proves rule-1 coverage failures retain declared jobs and checks frozen real
service and override evidence. Observer replay retains its rule-1-only behavior.

The Python capture API is `capture_snapshot(directory, domain, "audit")` in
`fleet_audit.capture` ("observer" is also accepted). It reads validated runbooks
and plists, then collects `/bin/launchctl print` for the domain and each job,
followed independently by `print-disabled`. Each command has a 10-second deadline
and a combined 4 MiB stream limit. Children are killed and reaped on limits.
No job programs run and no launchd state changes.

Pass the returned snapshot and a binary stdout stream to `emit_archive`.
It emits an uncompressed tar archive and writes no filesystem files. The
supervisor materializes it into a chosen directory, reviews `expected.json`,
and uses `load_snapshot(Path(directory))` and `replay(snapshot, "observer")`.
Members have bounded sizes, SHA-256 and source metadata. Logical absolute paths
are lookup keys only. Replay uses recorded evidence and clocks, with no live
fallback. Missing entries or unsafe references are invalid input; recorded
command or file failures remain evidence. Environment values are removed before
archive export; plist keys and command environment keys remain.

## Audit and freshness

```sh
uv run fleet-audit audit /absolute/runbook/directory --domain gui/501 --json
uv run fleet-audit audit /ignored --fixture fixtures/verdicts/completed-no-result
uv run python -m fleet_audit.capture audit /absolute/runbook/directory --domain gui/501
uv run python -m fleet_audit.acceptance verdicts --offline
```

Audit validates declarations before live collection, observes declared output,
then evaluates the fourteen rules in order. A running pid establishes process
presence only. Exit precedence is 3 (invalid input), 1 (definite finding),
2 (unresolved uncertainty), then 0 (nonempty, complete running, healthy idle,
or explicitly expected-disabled fleet). Unexpected disabled jobs exit 1;
ancillary collection errors on running jobs exit 2 unless another finding wins.
The audit fixture option uses snapshot domains and frozen observation times.

The ticks_jsonl v1 contract reads at most the final 64 KiB of a regular file,
removes exactly one terminal LF and parses only the last physical line. Blank,
oversized, malformed UTF-8/JSON, duplicate-key or nonobject final lines fail;
metadata changes before/after reading or path replacement yield uncertainty,
without retries. Same-metadata modifications may evade detection. The receipt
requires timezone-aware `ts`, Boolean `supervisor.ran`, null/integer/decimal-string
`rc`, and null/string `error`; optional `result` is null/string and never interpreted.
A tick completes when ran=false with null or `skipped:` error, or ran=true with
rc=0 and null error. Other non-null errors or a nonzero supervisor rc on ran=true
fail; other cases remain unestablished. Receipt age uses `ts`, never mtime or logs.
Freshness budgets come from the declaration: A<=M is fresh, M<A<=M+G is uncertain,
and A>M+G is late. Future timestamps are uncertain with no skew allowance.
Explicit mtime sufficiency is required for mtime-based healthy idle.

Increment 3 adds no drift comparison, scan verdicts, scan CLI/capture, or lab
adoption. Drift has not been computed; an empty comparison array does not prove
equality. Original stat-only spike evidence cannot prove receipt completion.
Capture includes receipt tail bytes and metadata in `receipts/index.json`, plus
output observations in `stats.json`. Capture placeholders have `reviewed: false`;
acceptance refuses them until expected assertions are reviewed. No receipt text
becomes a path or environment input. Replay opens only indexed snapshot members.
