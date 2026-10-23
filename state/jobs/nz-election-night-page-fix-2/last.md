Committed `eb4a0d0`; not pushed.

Implemented all six fixes: Chromium CI setup/fallback, phase-based countdown ordering, frame context and archive timestamp, separate replay announcements, nested-number XML parity, and the night placeholder gate.

Verification:
```text
pytest: 1911 passed, 2 errors
verify.py all: PASS all
bin/lint: lint ok (604 text files)
```

Both errors are sandbox Chromium launch failures. Host browser checks and screenshot inspection remain pending. Expected screenshot paths and full results are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-page/last.md), uncommitted.