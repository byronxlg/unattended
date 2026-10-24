Committed `5bc00f2`. Added guarded cron starts, tick watchdog, tests, and runbook instructions. Permissions unchanged; not pushed.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py
51 passed in 34.26s

bin/lint
lint ok (933 text files)

bash -n bin/tick
(no output, exit 0)
```

Review assumption: no existing upper closing bound was found. Added 8 November 06:00Z as the end of a 24-hour live window.

Uncommitted `last.md` records changed files, verification, and the sole moved trigger assertion.