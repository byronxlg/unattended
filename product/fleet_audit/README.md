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
