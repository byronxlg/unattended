Committed `7192300`; not pushed.

- Preflight requires explicit daily/cumulative header evidence.
- Shared CSV reader rejects malformed quoting before filtering rows or columns.
- Runbook documents reviewed supersession while preserving captures. No loader hook needed.
- Updated branch-owned tests and synthetic fixtures; protected tests unchanged.

Verification:

```text
Regression tests before: 7 failed
Regression tests after: 7 passed
test_advance.py: 108 passed in 16.68s
verify.py advance: PASS advance
bin/lint: lint ok (1028 text files)
```

Commands and failing output recorded in uncommitted `last.md`. Open questions: none.