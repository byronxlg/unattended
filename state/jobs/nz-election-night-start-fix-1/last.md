Committed `dcf30ad`; not pushed.

Added a 60-second watchdog timeout, serialized check/dispatch, a persistent success marker, and a clock recheck immediately before dispatch. Updated runbook and branch tests.

```text
bash -n bin/tick
(no output, exit 0)

uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py
54 passed in 37.05s

bin/lint
lint ok (934 text files)
```

Main’s tests were not edited by this fix. `last.md` remains uncommitted.