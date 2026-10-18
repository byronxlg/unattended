Committed `176944f`, not pushed. Added markets normalization/panel, daily automation, Pages trigger, tests and runbook. [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-7/last.md) remains untracked with full commands and test names.

`uv run --with pytest pytest -q product/nz_election`:
```text
531 passed in 205.58s (0:03:25)
```

Offline acceptance chain:
```text
Offline verification: immutable captures, not live data
PASS refresh: polls bundle
PASS refresh: daily bundles
PASS build: 79 routes
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS social
PASS home
PASS markets
PASS all
```

`bin/lint`: `lint ok (433 text files)`.

Pending supervisor checks: screenshots at 390/1280 and coalition browser run. Changed visible routes: `/` and `/downloads/`. No blocking questions.