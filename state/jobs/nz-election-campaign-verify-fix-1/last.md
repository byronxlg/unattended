Committed `7f027fb`, not pushed. Campaign failures now emit only owned codes. Added 26 marker-leak regressions; demonstrated the heading test failing on `eb27b19`.

Verification:

- Campaign tests: `121 passed`
- Full suite: `1 failed, 2145 passed, 2 errors` - the same three Chromium permission failures as baseline.
- Lint: `lint ok (875 text files)`
- Existing `pipeline/verify.py campaign`: `PASS campaign`. The prompt’s shorter path does not exist.

Proof and full commands are in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-campaign-verify/last.md). Browser tests still need a host run.