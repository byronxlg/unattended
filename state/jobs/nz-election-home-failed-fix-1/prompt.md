# Fix 1: nz-election-home-failed (PR #131)

The fresh review requested changes; the supervisor confirmed both items against the tree.

1. `product/nz_election/tests/test_home_failed.py:18` and `:40` set `state='failed'`. Production never writes it: `pipeline/export.py:223` accepts only fresh, stale, unavailable, and `pipeline/refresh.py:159` / `daily_refresh.py` write `stale` when data is retained and `unavailable` (with `last_success_at=None`) when it is not. Rewrite these cases with the real states and an `error_code`, so a regression keyed on `state == 'failed'` cannot pass them.
2. Absence coverage removes only the whole poll bundle. Add failed-refresh cases (state stale, error_code set) with retained data that is withheld, incoherent, and with mismatched average ids; each must show no hero figure and pass the absent-text check. The review's probes say the implementation already handles these; if one fails, fix `home.py`.

Constraints: `test_home_failed.py` is this branch's own test and moves with it. Tests on `main` at the branch base sha are not edited. No markup or class-name pins.

Done when, in the worktree:
`uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_home_failed.py product/nz_election/tests/test_home.py` passes (sandbox-denied Chromium cases may fail; name them), `bin/lint` prints `lint ok`, one commit on `change/nz-election-home-failed`, not pushed. Report in last.md.
