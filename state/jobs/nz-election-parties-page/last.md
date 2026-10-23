Committed `b389f5e`; not pushed.

Added parties page, sourced snapshots, navigation links and tests.

Verification:

- `uv run --with pytest pytest -q product`: **1841 passed, 2 errors**
- Populated `verify.py all`: **PASS all**
- `bin/lint`: **lint ok (619 text files)**

Both errors are Chromium launch permission failures. Screenshots, reference comparisons and visual question tests remain unverified.

Details in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-parties-page/last.md).