Committed `8951028`; not pushed.

Updated only the authorized browser assertion block. Fixed cached night notices to switch to neutral wording after the date.

Verification:
- Non-browser tests: **139 passed, 3 deselected**.
- Full command: **139 passed, 1 failed, 2 errors**, all three blocked by Chromium launch.
- `py_compile`: passed.
- Injected-clock client check: passed.
- `bin/lint`: **lint ok (990 text files)**.

Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-post-schedules/last.md), uncommitted. Host browser verification remains required.