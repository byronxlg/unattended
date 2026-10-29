# Follow-up 1: sunset notices equate stale with failed (PR #134 fresh review)

Two Important findings, both confirmed by the supervisor:

1. `product/nz_election/pipeline/build.py:280`: after the hourly sunset, the failure sentence is
   gated on `status['state'] != 'fresh'`. A stale status with no `error_code` now reports a failure
   it has no evidence for, and a stale status without `last_attempt_at` raises KeyError (origin/main
   renders). Invariant: "the update failed" appears only when the status carries failure evidence
   (`error_code`, as the pre-sunset branch already uses); no new required keys on the status row.
2. `product/nz_election/pipeline/market_panel.py:67`: same class. Stale-without-error and sparse
   `{'dataset': 'markets'}` statuses render "The last update failed." Gate it on the same evidence.

Add cases to your branch's tests (they move with the branch): stale status without error_code and
without last_attempt_at after each sunset (no failure sentence, no exception, retained data and the
"Scheduled updates ended" line still shown), and sparse markets status after the daily sunset.
Main's tests at the base sha are not to be edited. Assert visible text, not markup or classes.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py
product/nz_election/tests/test_polls_plan.py product/nz_election/tests/test_markets.py
product/nz_election/tests/test_home_failed.py` passes, the new cases fail at 131115b, and
`bin/lint` is ok. Commit in the worktree; do not push.
