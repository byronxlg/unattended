Committed `0f709cf`; not pushed.

Dispatch now requires shared state, holds the shared lock and reserves budget. Updated watchdog, starter, tests and runbook. Main’s tests remain unchanged.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_sunsets.py
171 passed in 75.33s

bin/lint
lint ok (1378 text files)
```

Baseline: `9 failed, 91 deselected`, asserting eight dispatches instead of six, invalid-ledger dispatches and dispatch at cutoff. No `TypeError`.

Failure lines recorded in uncommitted `last.md`. No open questions.