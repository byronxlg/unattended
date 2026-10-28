Committed `3babf1e`; not pushed.

Home now shares night’s stale/ended status logic, preserves counts, and initializes client freshness from the rendered capture time.

Verification:
- New regressions: 5 fail on `origin/main`, 5 pass with the fix.
- Requested pytest command: `9 failed, 110 passed`. All failures were sandbox-denied browser launches.
- `bin/lint`: `lint ok (1392 text files)`.

Blocked cases: handover `absent/zero/complete/recovery`, retirement `cached/waiting-after-stop`, design `map/trend/header`. Screenshots remain unverified.

[ last.md ](last.md) records the SHA, commands, output tails, and moved assertion.