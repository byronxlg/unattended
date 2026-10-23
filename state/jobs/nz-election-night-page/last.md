Committed `b2e960b`; not pushed.

Added national results, paused replay controls, persistent labels, static tables, XML parser and 20 screenshot states.

Verification:
```text
pytest: 1805 passed, 2 errors
verify.py all: PASS night; PASS all
bin/lint: lint ok (597 text files)
```

Not fully accepted:
- Chromium launch is sandbox-blocked, preventing browser checks and screenshot inspection.
- Packaged data lacks electorate leaders/margins, so the map/table remain absent.
- Existing 80-route set preserved.

Commands, outputs and gaps are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-page/last.md), uncommitted.