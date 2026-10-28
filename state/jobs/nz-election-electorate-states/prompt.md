# Build: electorate pages show post-election result states (readiness-7 item 1)

Page plan: intent/nz-election/pages/electorate.md
Design: product/nz_election/DESIGN.md (tokens and components; reuse existing status/caption styles, no new look)

## Goal
After polls close, an electorate page must say what state its local count is in. Today:
- product/nz_election/pipeline/electorate_pages.py:123 checks only the opening time, so stale, settled and official inputs all render "Who is leading here now?" and "leader provisional" with no freshness, ended or official status.
- electorate_pages.py:83 keeps "Who is standing in 2026?" through 27 November.

Use the shared result-state and freshness logic night/ and home use (pipeline/result_states.py, pipeline/sunsets.py; do not write a second copy), label a retained count with its capture time, say when counting has ended or results are official, and switch the candidate heading to past tense after the close.

## Read first
AGENTS.md, pipeline/electorate_pages.py, pipeline/result_states.py, pipeline/sunsets.py, pipeline/night_page.py (how it words each state), tests/test_electorate_page_plan.py, tests/test_sunsets.py.

## Constraints
- Do not edit pipeline/result_states.py, pipeline/night_page.py, pipeline/home.py, web/home-live.mjs or tools/check_workflow_history.py (open PRs #125, #126). Read them only.
- Tests on main at origin/main move only where they pin the old wrong wording; list moved assertions and why in last.md. Assert visible text and absence of "Who is leading here now?"/"leader provisional" in stale/settled/official states; do not pin markup or class names.
- Commit in the worktree; do not push.

## Done
- New cases at five clocks (before close, 7 Nov 10:00Z with a stale capture, 8 Nov 06:01Z, 14 Nov settled, 28 Nov official), each with the matching input; the post-close cases fail on origin/main and pass on HEAD.
- `uv run --with pytest pytest -q product/nz_election/tests/test_electorate_page_plan.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_design.py` all passed (list any sandbox-denied browser cases).
- `bin/lint` ok.
- last.md: commit sha, the command output tail, moved assertions.
