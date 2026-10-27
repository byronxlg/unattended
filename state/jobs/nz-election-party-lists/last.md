Committed `6ebf8bb`; not pushed.

Updated the snapshot, validator, renderer and tests with verified EC list sizes, source names and completeness.

Verification:
- Requested pytest command: `1 failed, 110 passed`.
- `python3 product/nz_election/pipeline/verify.py campaign`: `PASS campaign`.
- `bin/lint`: `lint ok (1087 text files)`.

Incomplete: macOS sandbox denied Chromium launch, blocking the existing picker test and required screenshots.

Details and remaining visual checks: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-party-lists/last.md). Report and artifacts remain untracked.