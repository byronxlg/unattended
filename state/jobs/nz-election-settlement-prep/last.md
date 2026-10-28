Committed `ce85ff3`; not pushed.

Added `settlement_capture.py`, updated `runbook/night.md`, and added tests in `test_result_import.py`. Import equality checks remain unchanged.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py product/nz_election/tests/test_result_states.py
1 failed, 91 passed in 237.15s
```

Only failure: existing browser test cannot launch Chromium under the sandbox (`Permission denied (1100)`).

Round-trip preparation/import passed with unchanged counts and provenance:

```text
PASS night
PASS waterfall
```

`bin/lint`: `lint ok (1298 text files)`.

Commands and results are recorded in uncommitted `last.md`. Remaining verification: run the browser test where Chromium launch is permitted.