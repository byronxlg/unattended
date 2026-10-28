Committed `c108291`; not pushed.

- `settlement_capture.py`: stable, sanitized `NIGHT_CAPTURE_PREP_FAILED`.
- `night.md`: explicit SHA assignments and substitutions.
- `test_settlement_capture.py`: eight malformed-input regressions.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_import*.py product/nz_election/tests/test_settlement*.py
58 passed in 212.14s (0:03:32)

Against a971810: 8 failed in 1.25s
After restoration: 8 passed in 0.57s

bin/lint
lint ok (1299 text files)
```

Commands and output recorded in `last.md`, left uncommitted. Open questions: none.