Committed `399812d`. Worktree clean; not pushed.

Changed: `drift.py`, models, loaded parser, reports, verdict rule 9, acceptance, `test_drift.py`, drift fixtures, both READMEs, and the single requested CI line. Existing tests and fixtures unchanged. No scan work or plan deviations.

From `product/fleet_audit/`:
```text
$ uv run python -m fleet_audit.acceptance registry --offline
OK registry
$ uv run python -m fleet_audit.acceptance observer --offline
OK observer
$ uv run python -m fleet_audit.acceptance verdicts --offline
OK verdicts
$ uv run python -m fleet_audit.acceptance drift --offline
OK drift
$ uv run --with pytest pytest -q
........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 72%]
........................................................................ [ 96%]
..........                                                               [100%]
298 passed in 1.56s
```

From worktree root:
```text
$ bin/lint
lint ok (132 text files)
$ uv run --with pytest pytest -q
no tests ran in 0.01s
$ rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit
product/fleet_audit/fleet_audit/collect.py
$ du -sh product/fleet_audit/.venv
1.0M	product/fleet_audit/.venv
```
Root pytest exited 5 as required; other verification commands exited 0. No open questions.