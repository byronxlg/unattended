Committed `5cc640b`; not pushed.

Updated home rendering, chart helpers, CSS, template, and checks: static charts, derived seat answer, 700 px column, one nav row, election night in More.

Verification:

- `uv run --with pytest pytest -q product/nz_election`: `670 passed in 305.08s`
- `verify.py all --data artifacts/home-design/data --site artifacts/home-design/after`: `PASS all`
- `bin/lint`: `lint ok (496 text files)`

Chromium launch was blocked by sandbox permissions. Screenshots, axe, and geometry remain unverified.

Details and before/after measures: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-design/last.md), uncommitted.