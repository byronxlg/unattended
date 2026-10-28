Committed `4186cd0`; not pushed.

Removed the obsolete voting timeline at handover, fixing duplicate `home-night` and `source-night` IDs. Browser harness now asserts uniqueness before and after cutoff.

Verification:
- Requested suite: `6 failed, 56 passed, 2 errors`, all failures/errors from Chromium sandbox denials.
- Blocked: handover `absent/zero/complete/recovery`, both retirement cases, XML parity, replay network check.
- DOM checks: `7 passed`; removing the fix triggers regression failures.
- Lint: `lint ok (1392 text files)`.

Host Chromium verification remains pending. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-stale/last.md).