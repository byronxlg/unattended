Committed `9c5c5fc`. Not pushed.

- `check_workflow_history.py`: date-specific cadence, restricted hourly gap checks, and guard detection limited to executable step commands.
- `test_harden.py`: added 24 cases; existing tests unchanged.
- `last.md`: records both regressions failing on `d891756` and final verification. Uncommitted.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden.py
144 passed in 0.23s

bin/lint
lint ok (996 text files)
```

All checks ran offline. Open questions: none.