Committed `ca77770`; not pushed.

- Capped legend connectors above label rows; added an overlap check.
- Directory assertion now counts electorate IDs, retaining exactly 71.
- Restored both page budgets; negative tests prove oversized explorer dependencies fail `/polls/`.

Verification:
- Root pytest: `580 passed in 196.72s (0:03:16)`
- Lint: `lint ok (420 text files)`
- Build: `PASS build: 79 routes`

**Screenshot acceptance remains blocked:** Chromium launch fails with `Permission denied (1100)`. No post-fix images were inspected or harness PASS claimed. Host verification still requires 79 routes, 219 images.

Per-item evidence and limitations: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home/last.md).