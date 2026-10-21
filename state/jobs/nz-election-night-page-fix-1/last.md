Committed `f02d0f4`; not pushed.

Fixed the timer phase bug in `night.mjs`: draws now start from playback interactions and include the endpoint. Browser assertions remain unchanged.

Verification:
- Node scheduler regression: fails on `ae48859` (frame 1), passes on HEAD (frame 2 at exactly 10,000 ms, stopped).
- Page tests: `5 passed, 2 errors`, both Chromium launch restrictions.
- Verifier: `PASS all`.
- Lint: `lint ok (604 text files)`.

Host browser verification remains pending. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-page/last.md), uncommitted.