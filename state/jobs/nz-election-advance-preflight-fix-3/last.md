Committed `4898e75`; not pushed.

Changed `advance_preflight.py` and tests. Unexpected CLI exceptions now produce fixed `INVALID_ADVANCE`, without traceback text. `MISSING_EVIDENCE`, `KeyboardInterrupt`, and `SystemExit` behavior is preserved.

Verification:

```text
Regression on d540336: 3 failed
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py
128 passed in 16.65s
bin/lint
lint ok (1028 text files)
```

Protected tests unchanged. Results recorded in uncommitted `last.md`. Open questions: none.