Committed `de641c1`; not pushed.

Rebuilt all 71 electorate pages, added boundary locators, updated provenance, styling and tests.

Verification:

- `uv run --with pytest pytest -q product`: **1948 passed, 1 failed, 2 errors**. All three are Chromium sandbox launch failures.
- Populated `verify.py all`: **PASS all**
- `bin/lint`: **lint ok (660 text files)**

Screenshots and the visual question test remain blocked by Chromium’s permission denial.

Details and assertion replacements: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-page/last.md), uncommitted.