# Build: home results show stale and ended status (readiness-6 item 1)

Page plan: intent/nz-election/pages/home.md
Design: product/nz_election/DESIGN.md (tokens and components; reuse the existing status/caption styles, no new look)

## Goal
On election night and after, the home results module must never call stale or ended counts "Live preliminary results". Today:
- 7 Nov 10:00Z, refresh fails: home still says "Live preliminary results", no stale warning (product/nz_election/web/home-live.mjs:7 passes no status callback).
- 8 Nov 06:01Z (after the live-loop stop), a populated home keeps that label (home-live.mjs:25 preserves results at cutoff).
- Fresh static builds with an unsettled capture keep it through 14 and 27 Nov (pipeline/home.py:205 uses the clock-independent fallback in pipeline/result_states.py:38).

Keep the counts. Render the same freshness and ended status night/ already uses (shared logic, not a second copy) in both the static home build and the client, and initialise client freshness from the rendered capture's time.

## Read first
AGENTS.md, product/nz_election/web/home-live.mjs, product/nz_election/web/night-live.mjs (its status handling), pipeline/home.py, pipeline/result_states.py, pipeline/sunsets.py, tests/test_home_handover.py, tests/home_handover_dom.mjs, tests/test_sunsets.py.

## Constraints
- Tests on main at origin/main move only where they pin the old wrong behaviour: home_handover_dom.mjs:65 expects unchanged HTML after cutoff; that expectation moves to the new status. Say which assertions moved and why in last.md. Do not pin markup or class names; assert visible text and absence of "Live preliminary results" in the stale/ended states.
- Do not touch files of open PRs: bin/night-watchdog, bin/tick, pipeline/night_start.py, pipeline/night_boundary.py, pipeline/fetch.py, tools/official_capture.py, runbook/night.md, .github/workflows/nz-election-night-rehearsal.yml.
- Commit in the worktree; do not push.

## Done
- New cases at clocks 7 Nov 10:00Z (failed refresh), 8 Nov 06:01Z, 14 Nov and 27 Nov with an unsettled capture; each fails on origin/main and passes on HEAD.
- `uv run --with pytest pytest -q product/nz_election/tests/test_home_handover.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_design.py` all passed (browser cases may be sandbox-denied; list them).
- `bin/lint` ok.
- last.md: commit sha, the command output tail, moved assertions.
