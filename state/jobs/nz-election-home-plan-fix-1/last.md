Committed `8d84eb5`, not pushed.

Fixed fold placement, mobile picker sizing, Māori column label, rendered-market test, duplicate link, and overdue-link targets.

Verification:
- Pytest: `1922 passed, 1 failed, 2 errors`
- Populated verification: `PASS all`
- Lint: `lint ok (644 text files)`

Chromium startup fails with macOS `Permission denied (1100)`, causing all three unsuccessful tests. Screenshots and cf770ea-fail/HEAD-pass target measurements remain blocked, so acceptance is incomplete.

Details and rerun instructions are in uncommitted [last.md](last.md).