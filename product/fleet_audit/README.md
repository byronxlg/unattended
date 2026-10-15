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
Paths and complete argument arrays are literal. No executable, working directory,
output, or receipt is opened. Environment observations contain keys only.

Increment 1 has no live observation, audit, scan, drift comparisons, freshness
checks, or health verdicts. A declared line proves only the registry and plist join.
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
service and override evidence. `declared` remains the only product CLI command;
this increment's section specifies no new product CLI command.

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

Only the rule-1 coverage guard is implemented. A passing guard has a null verdict,
not a health claim; observer reports exit 2. No freshness, receipt interpretation,
drift, audit/scan verdict engine, scan capture or audit/scan CLI ships here.
Receipt transport is deferred. Capture placeholders have `reviewed: false`;
acceptance refuses unreviewed expectations.
