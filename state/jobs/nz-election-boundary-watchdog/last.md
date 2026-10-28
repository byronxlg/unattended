Committed `a5dc4a6`, not pushed.

Changed `product/nz_election/pipeline/night_boundary.py` to supply isolated state and a lock file, exercise real locking and reservation, and verify the ledger at cutoff. Production watchdog and tests unchanged.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_night_boundary.py product/nz_election/tests/test_night_operation.py
146 passed in 104.63s (0:01:44)

python3 product/nz_election/pipeline/night_boundary.py
PASS watchdog-cutoff
PASS watchdog-queued-cutoff
```

All 29 drill scenarios passed.

```text
bin/lint
lint ok (1406 text files)
```

Report saved in uncommitted `last.md`. Open questions: none.