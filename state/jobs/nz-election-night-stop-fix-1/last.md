Committed `4c997ab`; not pushed. Worktree clean.

The page embeds the shared Python cutoff, which the client reads before its first tick. Added regression tests; existing tests unchanged.

Verification:

- On `95387fe`: all five regressions failed.
- Fixed targeted suite: `68 passed in 37.95s`.
- `uv run --with pytest pytest -q product/nz_election/tests`: `5 failed, 2464 passed, 2 errors in 645.79s`.
- `bin/lint`: `lint ok (967 text files)`.

All seven failures/errors were Chromium launch permission denials. Host browser verification remains open.

Report outside the worktree: [last.md](/tmp/nz-election-night-stop-fix1/last.md).