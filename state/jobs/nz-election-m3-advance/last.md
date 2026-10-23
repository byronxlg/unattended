Committed `6bbc873` on `change/nz-election-m3-advance`. Not pushed.

Implemented advance parsing, immutable captures, exports, campaign rendering, production gating and verification.

- Product pytest: `774 passed`
- `verify.py advance`: `PASS advance`
- `verify.py all --data … --site …`: `PASS all`
- `bin/lint`: `lint ok (531 text files)`

Both builds are under `/tmp/m3-advance/`. [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-m3-advance/last.md) contains exact commands, outputs and the main-branch regression proof; it remains uncommitted.

Open: real 2026 capture and host screenshots. Chromium launch was blocked by macOS sandbox permissions.