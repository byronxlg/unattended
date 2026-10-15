Committed `d00b16b`; clean worktree, nothing pushed.

Fixed `scan.py` and `receipts.py`; added only the two requested test functions to `tests/test_reports.py`. Existing tests and fixtures unchanged.

All required commands exited 0:

| Verification | Actual output |
|---|---|
| Acceptance `registry --offline` | `OK registry` |
| Acceptance `observer --offline` | `OK observer` |
| Acceptance `verdicts --offline` | `OK verdicts` |
| Acceptance `drift --offline` | `OK drift` |
| Acceptance `fleet --offline` | `OK fleet` |
| `uv run --with pytest pytest -q` | `313 passed in 1.76s` |
| `bin/lint` | `lint ok (141 text files)` |
| Subprocess import search | `product/fleet_audit/fleet_audit/collect.py` |

Nothing blocked or left undone.