Committed `18ab8ef`, not pushed. Updated night rendering, shared graphics, styles, live hooks and tests.

Verification:
- `bin/lint`: `lint ok (1115 text files)`
- Full pytest: `18 failed, 2883 passed, 2 errors`
- After fixes, `pytest --lf`: `14 failed, 4 passed, 2 errors`

All remaining failures/errors are Chromium launch denials. Screenshots, visual review and mobile overflow verification remain blocked.

Details and changed assertions: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-design/last.md).