Committed `58e918d`; not pushed.

Updated both harnesses, regression tests and runbook: selected-detail CORS, export provenance, waterfall checks, synthetic leader changes and reference retention. Historical replay unchanged.

Verification:
- Night pytest: `3 failed, 254 passed, 2 errors`. All five browser cases blocked by Chromium sandbox permissions.
- Excluding browser cases: `254 passed, 5 deselected`.
- `verify.py night`: `PASS night`
- `bin/lint`: `lint ok (1116 text files)`
- Origin/main regression comparison: `14 failed`, as expected.

Commands, failure lines and limitations are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-rehearsal-contract/last.md). Browser screenshots and deployed acceptance remain unverified.