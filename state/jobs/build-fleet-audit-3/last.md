Committed `145acd4`, `4c4f1fe`; worktree clean, nothing pushed.

Changed output/receipt handling, fourteen-rule verdict engine, audit CLI/reports, capture/replay, acceptance, fixtures, tests, READMEs, and the single CI line.

From `product/fleet_audit/`:
```text
$ uv run python -m fleet_audit.acceptance registry --offline
OK registry
$ uv run python -m fleet_audit.acceptance observer --offline
OK observer
$ uv run python -m fleet_audit.acceptance verdicts --offline
OK verdicts
$ uv run --with pytest pytest -q
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 81%]
.................................................                        [100%]
265 passed in 1.41s
```

From the worktree root:
```text
$ bin/lint
lint ok (126 text files)
$ uv run --with pytest pytest -q
no tests ran in 0.01s
$ rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit
product/fleet_audit/fleet_audit/collect.py
$ du -sh product/fleet_audit/.venv
1.0M	product/fleet_audit/.venv
```
Root pytest exited 5 as required; all other checks exited 0.

Plan notes: `runbook/fleet.md` is absent, so synthetic declarations use the spec’s contract. Missing `result` is accepted per decision 4 and the required no-result fixture. Updated the observer test’s rule-count assertion from 1 to 14; its coverage-only behavior remains tested. No drift or scan added.