Committed `bb5c46f` and `0608dd0`; no push. Worktree clean.

Added collector, structural parser, overrides, snapshot/capture, rule-1 verdict guard, fixtures and tests. Updated models, acceptance, READMEs and the single CI line. Existing AST test changed only to permit `collect.py`.

Verification from `product/fleet_audit/`:

```text
$ uv run python -m fleet_audit.acceptance registry --offline
OK registry
$ uv run python -m fleet_audit.acceptance observer --offline
OK observer
$ uv run --with pytest pytest -q
........................................................................ [ 32%]
........................................................................ [ 64%]
........................................................................ [ 96%]
........                                                                 [100%]
224 passed in 1.12s
```

From worktree root:

```text
$ bin/lint
lint ok (115 text files)
$ uv run --with pytest pytest -q
no tests ran in 0.01s
$ rg -l subprocess product/fleet_audit/fleet_audit
product/fleet_audit/fleet_audit/collect.py
$ du -sh product/fleet_audit/.venv
1.0M	product/fleet_audit/.venv
```

Root pytest exited 5 as required; other checks exited 0.

No plan deviations. Increment 2 names no new product CLI command, so none added. Receipt transport remains deferred; no verdict rules beyond coverage.