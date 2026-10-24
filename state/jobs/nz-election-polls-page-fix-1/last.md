Committed `93696cc`; not pushed.

Fixed neutral trend-label ticks, duplicate punctuation, leading-party change summary and `night/` hydration. The hydration defect also exists at base `27be8c1`.

Verification:

- New regressions: 5 failures on `280b2c2`; all 10 pass on HEAD.
- Full suite: `2034 passed, 1 failed, 2 errors`. Chromium blocked the party-picker test and two night browser tests.
- Live build: `PASS build: 81 routes`
- Verification: `PASS all`
- Lint: `lint ok (830 text files)`

Host screenshots and fold geometry remain unverified. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-polls-page/last.md), uncommitted alongside artifacts.