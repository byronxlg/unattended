Committed `6e1547b`; not pushed. Fixed all four findings with regression tests. No page, template or base-test changes.

Verification:
- Product suite: `1788 passed in 409.94s`
- Night verification: `PASS night`
- Lint: `lint ok (593 text files)`

Explicit `night --data` now requires the family. Aggregate `all` preserves optional families without printing a misleading `PASS night`.

`last.md` updated and left uncommitted.