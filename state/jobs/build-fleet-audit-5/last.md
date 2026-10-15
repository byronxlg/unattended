Committed `8109d44` and `e6e4600`; worktree clean, nothing pushed.

Changed package scan, CLI, reports, capture/replay, evidence handling, acceptance, `tests/test_reports.py`, fixtures and READMEs. CI adds only fleet acceptance. Earlier tests/fixtures and `runbook/` unchanged.

Package verification, all exit 0:

| Command | Actual output |
|---|---|
| `uv run python -m fleet_audit.acceptance registry --offline` | `OK registry` |
| `uv run python -m fleet_audit.acceptance observer --offline` | `OK observer` |
| `uv run python -m fleet_audit.acceptance verdicts --offline` | `OK verdicts` |
| `uv run python -m fleet_audit.acceptance drift --offline` | `OK drift` |
| `uv run python -m fleet_audit.acceptance fleet --offline` | `OK fleet` |
| `uv run --with pytest pytest -q` | `311 passed in 1.72s` |

`uv run fleet-audit --help` output, exit 0:
```text
usage: fleet-audit [-h] {declared,audit,scan} ...

Validate declarations, audit contracts, or scan user LaunchAgents.

positional arguments:
  {declared,audit,scan}
    declared            validate runbooks and their plist labels
    audit               audit declared jobs and freshness
    scan                observe non-Apple user LaunchAgents without contracts

options:
  -h, --help            show this help message and exit
```

Root verification:

| Command | Actual output | Exit |
|---|---|---|
| `bin/lint` | `lint ok (141 text files)` | 0 |
| `uv run --with pytest pytest -q` | `no tests ran in 0.01s` | 5 |
| `rg -l '^(import\|from) subprocess' product/fleet_audit/fleet_audit` | `product/fleet_audit/fleet_audit/collect.py` | 0 |
| `du -sh product/fleet_audit/.venv` | `1.0M product/fleet_audit/.venv` | 0 |

No implementation deviations. Live verification, independent review and publication remain supervisor tasks.