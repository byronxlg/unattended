Committed `b4535af`; not pushed.

Source tracing identifies screenshot caret cleanup leaving `style=""` on the search input. Moved baseline capture after screenshots. Whole-HTML equality and renamed-not-shown checks remain intact; client and main tests unchanged.

Verification:
- Requested filter: `250 passed, 8 deselected, 1 error` from a browser fixture.
- Excluding that browser case: `250 passed, 9 deselected`.
- Lint: `lint ok (1116 text files)`.

Chromium remains sandbox-blocked. Diagnosis and verification details are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-rehearsal-contract/last.md).