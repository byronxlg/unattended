Committed `ed64b0d`; not pushed.

Worker now inherits the lock descriptor. SIGKILL regression tests fail on `dcf30ad` and pass with the fix, including uv-launched workers.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py
56 passed in 44.28s

bash -n bin/tick
(no output, exit 0)

bin/lint
lint ok (934 text files)
```

Existing tests unchanged. Runbook updated; `last.md` remains uncommitted.