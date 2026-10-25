Committed `d2538ee`; not pushed.

`verify.py` now checks required-family presence before bundle/site validation. Added `test_verify_missing_index.py`; protected tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_verify*.py product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_campaign_verify.py product/nz_election/tests/test_night.py
313 passed in 304.88s (0:05:04)

bin/lint
lint ok (979 text files)
```

New regressions: 11 failed on `617dd80`; all 12 pass after the fix.

`last.md` records the commit, commands, outputs, and failing baseline cases. Left uncommitted. Open questions: none.