**Request changes.**

- **Important** [build.py:280](/Users/byron/repos/unattended/.worktrees/nz-election-sunset-surfaces/product/nz_election/pipeline/build.py:280): `state != 'fresh'` does not establish collection failure. A stale status with `error_code=None` now falsely reports failure. If that status lacks `last_attempt_at`, HEAD raises `KeyError`; origin/main renders normally. Preserve the existing `error_code` guard. Missing `state` or `last_success_at` already failed before this change.
- **Important** [market_panel.py:67](/Users/byron/repos/unattended/.worktrees/nz-election-sunset-surfaces/product/nz_election/pipeline/market_panel.py:67): Stale-without-error and sparse `{'dataset': 'markets'}` statuses both falsely render “The last update failed.” Gate this sentence on actual failure evidence.

The new tests assert visible wording and retained data rather than markup/classes, cover the requested clocks with healthy/failed cases, and their post-sunset assertions would fail against origin/main. However, both equate stale with failed, leaving these regressions uncovered. Add stale-without-error and sparse-status cases.

Read-only Python probes reported:
```text
polls missing attempt HEAD: KeyError: 'last_attempt_at'
PASS: 26 healthy/failed clock and baseline comparisons
```
Pre-sunset output matched origin/main byte-for-byte in those comparisons. Daily sunset is **14 Nov 11:00Z** per `sunsets.py`; remaining active at 14 Nov 00:00Z is correct.

Verification limits:
- `git fetch origin`: blocked writing `FETCH_HEAD`; reviewed cached `origin/main...HEAD` at `131115b`.
- `uv run --with pytest pytest -q product/nz_election/tests/test_polls_plan.py product/nz_election/tests/test_markets.py`: blocked initializing the UV cache.
- No screenshots taken. No files changed.