# Build: empty night page picks up the first live capture without reload (readiness-7 item 2)

Page plan: intent/nz-election/pages/night.md
Design: product/nz_election/DESIGN.md (tokens and components; reuse existing status styles, no new look)

## Base
This worktree is stacked on change/nz-election-home-stale (PR #126, which edits night_page.py and result_states.py). Build on it; it will be retargeted to main after #126 merges.

## Goal
product/nz_election/pipeline/night_page.py:144 returns before emitting the live target, the status element and the night-live.mjs client when the night family is absent. A reader who opens night/ while the first acquisition is failing stays on the empty page after publication recovers. Emit the live shell and client even with no sequences, with explicit waiting copy before results and ended copy after the cutoff, and the official EC results link. The client must render the first complete package without navigation and stop polling at the shared cutoff (pipeline/sunsets.py; zero requests past it).

## Read first
AGENTS.md, pipeline/night_page.py, web/night-live.mjs, pipeline/sunsets.py, pipeline/result_states.py, tests/test_night_page.py, tests/night_live_browser.py.

## Constraints
- Do not edit pipeline/home.py, web/home-live.mjs, tests/test_home_handover.py, tests/home_handover_*.{py,mjs} (PR #126's own), or tools/check_workflow_history.py (PR #125).
- Tests on main move only where they pin the old empty-page behaviour; list them and why in last.md. Assert visible text, requests and rendered counts, not markup or class names.
- Commit in the worktree; do not push.

## Done
- A browser case: night/ built with no night family, served responses unavailable then a first complete package; page shows waiting copy, then the counts without navigation; polling stops at the cutoff. It fails on the base commit 0670b2d and passes on HEAD. A static case: at 8 Nov 06:01Z the empty page shows ended copy and the official link, and no client request is made.
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_design.py` all passed (list sandbox-denied browser cases).
- `bin/lint` ok.
- last.md: commit sha, the command output tail, moved assertions.
