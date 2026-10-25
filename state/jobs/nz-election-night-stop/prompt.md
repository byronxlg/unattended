# Build: bounded stop for the election night loop (plan-week-after increment 1, second half)

Page plan: intent/nz-election/pages/night.md (no page change expected; the cited plan is for the gate and for the copy shown when the loop has stopped).

## Goal

PR #78 (merged c2ce1fc) starts the five-minute night-live loop on its own. Nothing stops it: night-live chains a successor indefinitely and the client polls forever. Add an explicit, tested stop.

Invariants (choose the mechanism):
1. No night-live run fetches, publishes or dispatches a successor after the stop instant. The stop instant is one named constant, default 2026-11-08T06:00:00Z (the proposal in a NOTE to Byron; it may move, so it must be a one-line change with the tests following the constant, not a literal repeated across files).
2. A run already in flight at the stop instant finishes its current publish and exits 0 without a successor; the stop is checked at the decision to chain, not only at start.
3. After the stop, the published bundle says the loop has ended (a field the client reads), and web/night-live.mjs stops polling when it sees it. Page copy for that state follows pages/night.md and the existing absent-text rule (no "not available" wording).
4. The bin/tick night watchdog and night_start.py never dispatch after the stop instant (they already respect the closing boundary; make them use the same constant).
5. Manual workflow_dispatch after the stop exits 0 with a one-line log saying the loop has ended, so the 27 Nov official import path is not blocked by it (official import is a separate path; do not change it).

## Read first

AGENTS.md, intent/nz-election/plan-week-after.md (increment 1), product/nz_election/pipeline/night_live.py, night_start.py, bin/night-watchdog, the night_live section of bin/tick, .github/workflows/nz-election-night-live.yml, web/night-live.mjs, product/nz_election/runbook/night.md, product/nz_election/tests/test_night_operation.py.

## Constraints

- Branch change/nz-election-night-stop stacks on change/nz-election-results-states (result states, PR to follow); do not rewrite its commits.
- Tests on main at c2ce1fc are protected except where they pin the old unbounded behaviour; name any such test in last.md with the reason. This branch's own tests move with it.
- Injected clocks only; no sleeps, no network.
- Runbook: one section "Stop" naming the constant, how to move it, and how to restart after the stop if Byron asks.

## Done

- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py` passes, with new tests for 06:00Z minus one second (chains), plus one second (no fetch, no successor), an in-flight run crossing the instant, the watchdog and night_start after the stop, and the client stop field.
- `uv run --with pytest pytest -q` whole suite: report counts; browser tests may fail in the sandbox on Chromium launch, say which.
- `uv run product/nz_election/pipeline/verify.py night` PASS; `bin/lint` ok; `bash -n bin/tick` ok.
- Commit in the worktree, do not push. last.md: what changed, the constant's location, test counts.
