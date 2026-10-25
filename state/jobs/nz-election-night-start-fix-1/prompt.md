# Fix 1 for PR #78 (nz-election-night-start), on the build thread

Fresh review requested changes; the supervisor confirmed all three items against bin/tick at 5bc00f2.
The full review is state/jobs/review-nz-election-night-start/last.md in the main checkout.

1. Bound the whole watchdog operation (uv startup, eligibility check, gh workflow run), not only
   `gh run list`. A stall must not delay the rest of the tick: give the whole step a hard wall
   clock limit (for example 60 s total) and continue the tick when it is hit, with a log line.
2. Serialize check and dispatch across overlapping ticks (a lock, e.g. mkdir or flock-style
   lock under state/, released on exit including timeout), and keep a successful-dispatch marker
   (state/, gitignored like the other run markers) so a second tick inside the run-list
   visibility lag does not dispatch again. Define how long the marker suppresses a redispatch
   and say it in the runbook.
3. Make the closing boundary hold at dispatch time, not only at decision time: the clock check
   that admits a dispatch is re-made immediately before `gh workflow run` (or the dispatch is
   inside the same bounded, clock-aware operation), so a decision at 2026-11-08 05:59:59Z cannot
   dispatch after 06:00Z.

Tests: add tests for a blocking eligibility check or dispatch (tick continues within the bound),
two overlapping invocations (one dispatch), the marker suppressing a redispatch, and the
05:59:59Z to 06:00Z transition (no dispatch). The branch's own tests move with the change; tests
on main at e5812e3 are not edited.

Done when, in the worktree:
- `bash -n bin/tick` prints nothing
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py` passes, including the new tests
- `bin/lint` prints ok
Commit on change/nz-election-night-start; do not push; do not commit last.md.
