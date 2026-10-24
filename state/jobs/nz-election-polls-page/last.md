Committed `280b2c2`, not pushed.

Rebuilt polls/ with ordered answers, shared charts, preserved fragments and updated tests.

Verification:

- `uv run --with pytest pytest -q product`: `1 failed, 2024 passed, 2 errors`; all three are Chromium launch denials.
- Live-data build: `PASS build: 81 routes`
- `verify.py all`: `PASS all`
- `bin/lint`: `lint ok (829 text files)`

Screenshots and visual question test require a host run: Chromium reports `Permission denied (1100)`.

[Last report](/Users/byron/repos/unattended/.worktrees/nz-election-polls-page/last.md) records commands, fragments and the live allocation’s 67-seat majority. Report and artifacts remain uncommitted.