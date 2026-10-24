# Build: start election-night live mode without a human (nz-election-night-start)

Change: nz-election. Intent: intent/nz-election/intent.md, spec: intent/nz-election/spec.md,
plan: intent/nz-election/plan-m3.md (increment 5 operation). Page plan: intent/nz-election/pages/night.md
(no page or template change in this job; workflow and loop tooling only).

## Goal
`nz-election-night-live.yml` has no cron (runbook/night.md:150-158): someone must dispatch it at
7 Nov 06:00Z. Byron is away and the supervisor runs on a 10 minute tick that has been down for
hours before. Make the start automatic, with two independent triggers, and safe outside the night.

1. Workflow: add a `schedule` trigger near 7 Nov 2026 06:00Z (for example `2 6 7 11 *` plus one
   backup a few minutes later; GitHub cron drifts, see bin/tick:53). A scheduled run must be a
   no-op success (no acquisition, no publication, no chaining) unless the injected-clock guard
   says the 2026 live window is open: before 2026-11-07T06:00Z, after the existing close gate, or
   in any later year. Scheduled runs are never rehearsals. Reuse the existing guard in
   `pipeline/night_live.py`; do not add a second clock.
2. `bin/tick`: a watchdog in the style of `watchdog()` (bin/tick:59-67): from 2026-11-07T06:10Z
   until the close gate, if no night-live run has been created since 06:00Z 7 Nov, dispatch it
   once with `gh workflow run nz-election-night-live.yml --ref main` and log a line. Never
   dispatch outside that window, never when one is queued or in progress. Keep it short.
3. Runbook: update runbook/night.md "There is no cron" and the dispatch steps to say what starts
   it now and how to stop it (disable the workflow).

Read first: .github/workflows/nz-election-night-live.yml, pipeline/night_live.py (guard),
runbook/night.md, tests/test_night_operation.py, tests/test_workflows.py, bin/tick.

## Constraints
- Contracts in tests on main at the base sha move only where they pin the trigger set of this
  workflow; say which in last.md. Nothing weaker; no other workflow changes.
- No secrets; permissions block unchanged.

## Done
- New tests: scheduled event before 06:00Z 7 Nov 2026, after close, and in 2027 exits 0 doing
  nothing (transport never called); at 06:02Z 7 Nov 2026 it proceeds to acquisition; the bin/tick
  window logic is testable (factor the time and run-list check into a small function or script
  with an injected clock and test it).
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py`
  passes; `bin/lint` prints ok; `bash -n bin/tick` clean.
- Commit in the worktree; last.md lists changed files, tests, and any moved assertion.
