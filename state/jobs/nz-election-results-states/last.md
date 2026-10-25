Committed `109e2b6`, not pushed: result-state pipeline, pinned baseline, home/night copy, terminal polling, fixtures, tests, and runbook commands.

Verification:

- `uv run --with pytest pytest -q product/nz_election/tests`: **2414 passed, 5 failed, 2 errors**. All failures/errors are Chromium launch permission failures.
- `uv run product/nz_election/pipeline/verify.py night`: `PASS night`
- `uv run product/nz_election/pipeline/verify.py waterfall`: `PASS waterfall`
- `bin/lint`: `lint ok (937 text files)`

Eight screenshots and visual question tests remain blocked by browser permissions. Details and logs: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-results-states/last.md).