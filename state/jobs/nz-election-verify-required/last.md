Committed `617dd80`. No push.

- `verify.py`: explicit SKIP lines, `--require`, safe missing-family errors.
- `runbook/night.md`: requires `night,waterfall` from 7 November.
- Added `test_verify_required.py`; existing tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_verify*.py product/nz_election/tests/test_night_operation.py
89 passed in 368.79s (0:06:08)

bin/lint
lint ok (978 text files)
```

Additional campaign/night tests: 212 passed. Regression test confirmed failing on `7ecf80a`.

`last.md` contains the commit SHA, counts, exact CLI stdout and exit codes. Left uncommitted.

Open questions: none.