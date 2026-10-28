Committed `ac8d50a`; not pushed.

Changed watchdog, starter, tick comment, runbook start section and tests. Recovery allows six attempts per night, with ten-minute grace. Existing guards and tests remain unchanged.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_sunsets.py
168 passed in 72.11s
```

New cases against both files at `1d1d9fa`:

```text
pytest -q product/nz_election/tests/test_night_operation.py -k dead_loop --tb=no
18 failed, 12 passed, 67 deselected
```

`bin/lint`: `lint ok (1378 text files)`. Python compilation and `bash -n bin/tick` passed.

Outstanding check: `bash -n bin/night-watchdog bin/tick` fails because `night-watchdog` is Python. Details and results recorded in uncommitted `last.md`.