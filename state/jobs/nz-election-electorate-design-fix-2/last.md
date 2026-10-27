Committed `d6d8c0f`, not pushed. Added compact phone candidate rows, repaired empty-list map destinations, and added behavioural browser checks.

Verification:
- Required pytest command: **129 passed, 11 failed**, all failures from Chromium sandbox launch denials.
- Empty-candidate regression: failed on `9488223`, now passes across 71 seats.
- `bin/lint`: `lint ok (1143 text files)`.

Browser fold checks and screenshots remain unverified due to launch denials. Commands and outputs are recorded in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-design/last.md), left uncommitted.