# Fix round 3 for PR #76 (night deployed probe)

The third fresh review requested changes, one Important, confirmed by the supervisor. Fix job on
change/nz-election-night-deployed: tests on main at the base sha f406321 do not change; this branch's
own tests (test_night_deployed.py) move with the fix. Nothing weakens a check.

1. `product/nz_election/tests/night_deployed.py:225` `probe_phase` takes `now_ms` from `Date.now()` in
   the page's JavaScript context, which page code can override. With page time pre-close and real time
   post-close, zero night data responses pass. Decide the phase from the host clock (Python, UTC,
   injectable for tests); keep reading the schedule from `night-live.mjs` as now. The record may keep
   the page's clock as a second, informational field, never as the deciding one.
   Add a regression: host time after close, page `Date.now` overridden to before close, zero responses
   gives FAIL. It must fail on 2ff2d4f.

Definition of done (paste each output in last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py` passes (if the
  sandbox has no Chromium, say which tests skipped; the supervisor runs them on the host), and the new
  regression fails on 2ff2d4f.
- `bin/lint` prints ok.
Commit on the branch; do not push.
