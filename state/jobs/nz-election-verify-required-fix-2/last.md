Committed `0c61278`; not pushed.

`verify.py` now checks both supplied locations before validation. Added eight combined-flags regressions; all fail on `d2538ee` and pass after the fix. Protected tests untouched.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_verify_missing_index.py
20 passed in 3.84s

uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py
63 passed in 37.39s

bin/lint
lint ok (979 text files)
```

Existing optional-family SKIP test: 1 passed.

`last.md` records the evidence and remains uncommitted. Open questions: none.