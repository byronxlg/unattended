Committed `ec403fc`; only the requested test file changed. Nothing pushed.

Verification:
- Pytest: **40 passed, 4 failed**.
- One failure exposes incorrect product order: enrolment and Policy.nz precede candidates.
- Three failures are Chromium sandbox launch denials.
- Requested `rg`: no matches.
- Lint: `lint ok (1142 text files)`.

Product code remains unchanged. Acceptance blockers and command output are recorded in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-design/last.md).