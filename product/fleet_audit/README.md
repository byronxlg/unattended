# Fleet Audit

Read-only Python 3.12 CLI for the current user's launchd GUI domain. Runtime
requires only PyYAML 6.0.2. From `product/fleet_audit`, install with
`uv sync --locked`; `uv run fleet-audit --help` lists the commands.

## Commands

`declared` validates version 1 Markdown frontmatter and joins each declaration to
its plist Label. It collects no service, output or receipt evidence.

```sh
uv run fleet-audit declared /Users/byron/repos/unattended/runbook/fleet
```

`audit` validates first, then observes services, effective disablement, declared
outputs, receipt completion and three-way drift. Invalid input prevents live
collection. Explicit domains must match the current user and declarations.

```sh
uv run fleet-audit audit /Users/byron/repos/unattended/runbook/fleet --domain gui/501 --json
```

`scan` enumerates `~/Library/LaunchAgents` without a runbook. A valid Label
beginning `com.apple.` is excluded. Unreadable or no-label plists are excluded
only when the filename begins `com.apple.`. Other no-label rows remain identified
by path; filenames never become service labels and those rows have no lookup.

```sh
uv run fleet-audit scan --domain gui/501
```

Scan reports `running`, `failing`, `disabled`, `loaded_disabled`, or
`cannot_determine`. It stats only plist-declared stdout/stderr paths, once per
unique path across the fleet, without reading their contents. It invents no
freshness contract, deadline, receipt or drift expectation. Idle interval jobs
remain uncertain. Running with a pid establishes process presence, not useful
work; an old log cannot override it. Scan does not inspect system LaunchDaemons,
cron, other users, executables or working directories. It never runs job programs
or changes launchd state.

A declaration directory contains declarations only. Use `runbook/fleet`, where
the supervisor's lab declaration lives at `runbook/fleet/fleet.md`. Do not point
at `runbook/`: its management frontmatter uses a different schema and correctly
fails validation. Discovery validates every frontmatter-bearing Markdown file.
The lab declares interval 600, receipt maximum age 1200 and grace 1800 seconds;
RunAtLoad is observed but is not a declared expectation.

## Reports and exits

All three commands accept `--json`. Text has one escaped line per job, followed
by drift and uncertainty details, issues and a summary. Invalid declared text
reports go to stderr. JSON is one document with schema_version, command, domain,
observed_at, jobs, issues, summary and exit_code. It includes explicit unknowns,
unattempted observations, UTC timestamps, ordered argv and observation references.
Environment keys can appear; environment values are removed.

Exit precedence is **3, 1, 2, 0**:

- **3**: invalid CLI, declaration, plist join or snapshot.
- **1**: failing, late, declared_not_loaded, loaded_disabled, drift or unexpected disablement.
- **2**: unresolved uncertainty, incomplete/empty coverage or ancillary errors.
  Scan disabled has unknown intent and exits 2 unless a definite finding wins.
- **0**: a nonempty complete fleet containing only running, healthy_idle or
  explicitly expected-disabled jobs, without drift or uncertainty. Declared
  returns 0 only for a valid nonempty registry.

Audit compares each requested program, complete argv, directory and schedule
component across registry-to-disk, registry-to-loaded and disk-to-loaded.
Unknown comparisons are incomplete, never equal. Loaded policies are not
inferred from disk for drift. Paths and argv remain literal, without expansion
or shell splitting. Drift survives a running or failing verdict.

The ticks_jsonl v1 contract parses only the final physical line within a bounded
64 KiB tail. A tick completes when ran=false with null or `skipped:` error, or
ran=true with rc=0 and null error. Result text is never a success enum.
Malformed final lines and concurrent modifications remain uncertain. Receipt
age uses its timestamp, not log age or mtime. A<=M is fresh, M<A<=M+G is uncertain,
and A>M+G is late. Future timestamps are uncertain. Mtime-based healthy_idle
requires explicit mtime sufficiency. Sequential collection is not atomic;
cross-version launchctl compatibility and supervisor semantic success are not shown.

## Snapshots and verification

Audit and scan accept `--fixture <snapshot-directory>`. Replay uses only indexed
members and frozen times: no original-path reads, commands or live clock.
Missing members are invalid input; recorded observation failures remain evidence.
Real stat projections with unavailable sizes retain null, never an invented zero.

Supervisor capture emits an uncompressed tar stream to stdout and diagnostics
to stderr. Materialization and live report publication are supervisor tasks.

```sh
uv run python -m fleet_audit.capture audit /Users/byron/repos/unattended/runbook/fleet --domain gui/501
uv run python -m fleet_audit.capture scan --domain gui/501
```

Commands have a 10-second deadline and 4 MiB combined stream bound. Capture
redacts environment values before archiving, includes member hashes/provenance,
and emits `expected.json` with `reviewed: false`. Acceptance refuses unreviewed
expectations. Review assertions independently before using a capture for acceptance.

```sh
uv run python -m fleet_audit.acceptance registry --offline
uv run python -m fleet_audit.acceptance observer --offline
uv run python -m fleet_audit.acceptance verdicts --offline
uv run python -m fleet_audit.acceptance drift --offline
uv run python -m fleet_audit.acceptance fleet --offline
uv run --with pytest pytest -q
```

Run `bin/lint` from the repository root. See `fixtures/README.md` for sources,
synthetic transformations and timestamp limitations. Earlier installation
measurement: PyYAML files 849,283 bytes including metadata and bytecode; the
build backend is pinned to setuptools 75.8.0 and is not a runtime dependency.
