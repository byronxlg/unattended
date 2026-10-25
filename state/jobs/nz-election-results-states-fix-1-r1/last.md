Committed `3f507da` and `84f8da5`; not pushed. Added official-source provenance validation, DOM handover copy updates, and named-leader mobile search coverage.

Verification:

- Regression: fails on `739f880`, passes on HEAD.
- Targeted tests: `41 passed, 1 deselected`.
- Verifiers: `PASS night`, `PASS waterfall`.
- Lint: `lint ok (949 text files)`.
- Full suite: `2439 passed, 5 failed, 2 errors`.

All seven failures/errors were Chromium launch failures: macOS `Permission denied (1100)`. Browser assertions and fresh screenshots remain unverified.

Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-results-states/last.md), left uncommitted.