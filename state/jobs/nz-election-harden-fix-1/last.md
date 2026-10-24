Committed `a67a6fa`, not pushed. Fixed all four items: missing eval detection, zero-exit SKIP/FAIL rejection, PARTIAL without history, and hourly/daily recovery policies.

Verification:
- `test_harden.py`: **80 passed**
- `bin/lint`: **lint ok (903 text files)**
- Against `5835b0e`: all **8 regression cases fail**, confirming coverage.

Results recorded in uncommitted `last.md`. Base tests unchanged.