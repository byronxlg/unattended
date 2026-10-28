# Build: detect and recover a dead live loop (nz-election-night-recovery)

Goal: on election night (7 Nov NZ) Claude operates alone (Codex ends 7 Nov 03:14Z). Today a failed first
night-live run suppresses the watchdog's recovery, and a successor dispatch can fail after a loop run finishes,
leaving no live loop and nothing that notices. Make the watchdog notice and recover, bounded by the existing cutoff.
Evidence (readiness audit at 6afa95d): `product/nz_election/pipeline/night_start.py:22` (`should_start` returns
False once any run exists after END, including a failed one), `pipeline/night_live.py:307` and `:326` (successor
dispatch after the loop).

Read first: `AGENTS.md`; `bin/night-watchdog`; `bin/tick` (watchdog call site); `pipeline/night_start.py`;
`pipeline/night_live.py`; `.github/workflows/nz-election-night-live.yml`; `tests/test_night_operation.py`
(`test_scheduled_open_acquires_production`, `test_night_watchdog_window`, the cutoff and lock tests);
`runbook/night.md` (start, watchdog and stop sections).

Invariant (you choose the shape): between the night start and the 8 Nov 06:00Z cutoff, if no night-live run is
queued or in progress and the newest run concluded other than success (or its successor never appeared within a
bounded grace), the watchdog dispatches exactly one new run; a bounded number of recoveries per window (say so and
why); never a duplicate while one is queued/in progress; never at or after the cutoff; the lock and the
fail-closed clock behaviour stay as they are.

Constraints:
- Every production guard stays (freeze, sunsets, cutoff, lock). Do not move a constant or clock to simulate.
- Tests on main at 1d1d9fa stay untouched unless a contract genuinely moves with the new behaviour; if one does,
  name it in last.md with the reason. Add new cases: failed first run recovers, failed/missing successor recovers,
  pending or in-progress run suppresses, at/after cutoff nothing dispatches, the recovery bound holds.
- Runbook: edit only the night-live start/watchdog part of `runbook/night.md` (another job edits the settled and
  official section): what the watchdog now does, the log line it prints, and the manual recovery command Claude runs
  if the watchdog itself is down.
- No network in tests (inject `gh` output / transport).

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_sunsets.py`
  passes (report counts) and the new cases fail with `night_start.py` (and `bin/night-watchdog`) at 1d1d9fa
  (show that run).
- `bash -n bin/night-watchdog bin/tick` and `bin/lint` pass.
- Commit on this branch; do not push. last.md lists the files changed, the counts, and the recovery bound chosen.
