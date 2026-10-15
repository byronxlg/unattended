Committed `e2c946e`; clean worktree, nothing pushed. Fixtures and existing tests unchanged.

All required verification commands exited 0:

| Check | Actual output |
|---|---|
| Acceptance registry | `OK registry` |
| Acceptance observer | `OK observer` |
| Acceptance verdicts | `OK verdicts` |
| Acceptance drift | `OK drift` |
| Acceptance fleet | `OK fleet` |
| Package pytest | `315 passed in 1.70s` |
| `bin/lint` | `lint ok (141 text files)` |
| Subprocess import search | `product/fleet_audit/fleet_audit/collect.py` |

`git diff --stat d00b16b`: only `fleet_audit/scan.py`, `fleet_audit/files.py`, and `tests/test_reports.py`; `3 files changed, 64 insertions(+), 5 deletions(-)`.

Nothing blocked or left undone.