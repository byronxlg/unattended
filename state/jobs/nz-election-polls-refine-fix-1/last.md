Committed `ebce3c7`; not pushed.

Client lanes now read abbreviations supplied by the server’s shared helper. Added seven-party markup parity tests.

Verification:
- On `e9ca98d`: `2 failed`.
- On HEAD: `2 passed, 1 deselected`.
- `bin/lint`: `lint ok (859 text files)`.
- Full suite: `2039 passed, 1 failed, 2 errors`. All three blocked by Chromium launch permissions; zero skips.
- Standalone coalition browser check also blocked, not skipped.

Evidence in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-polls-refine/last.md). Host browser verification remains.