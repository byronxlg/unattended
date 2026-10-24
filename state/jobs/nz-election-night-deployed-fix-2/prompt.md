# Fix round 2 for PR #76 (night deployed probe)

The second fresh review requested changes, one Important. Fix job on change/nz-election-night-deployed:
tests on main at the base sha f406321 do not change; this branch's own tests (test_night_deployed.py)
move with the fix. Nothing weakens a check.

1. `product/nz_election/tests/night_deployed.py:243` `night-data-transport` passes with zero responses
   whatever the phase, and page errors do not fail probe mode, so a broken live init that leaves the
   static fallback still gives PASS. Make it phase-aware, from the same schedule the page uses:
   - before polls close: zero night data requests passes only when the page shows its before-close
     state (the countdown and the vote/ link) and there are no unexpected page errors; the record
     names the phase.
   - from polls close: require at least one successful, validated night data response after opening;
     zero responses, pending or inconclusive transport is FAIL.
   - unexpected page errors (pageerror, console error from the page's own scripts) fail the probe in
     every mode, listed in the record.
   Add tests with injected pages or recorded responses for: after close with zero responses (FAIL),
   after close with one valid response (PASS), before close with a page error (FAIL), before close
   clean (PASS).

Definition of done (paste each output in last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py` passes (if the
  sandbox has no Chromium, say which tests skipped; the supervisor runs them on the host), and the new
  tests fail on 36659a4.
- `bin/lint` prints ok.
- Commit on the branch, do not push. Do not commit last.md.
