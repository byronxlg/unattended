# Build: workflow-history acceptance honours collection sunsets (readiness-6 item 2)

## Goal
product/nz_election/tools/check_workflow_history.py derives each workflow's active window from its text (freeze and night guards) but ignores the collection sunsets in pipeline/sunsets.py (hourly, daily, social), at line 258. So week-after acceptance demands hourly runs after collection ended: a probe showed hourly required for the whole 2026-11-14T06:00Z to 2026-11-27T06:00Z interval. Green no-op runs pass; disabling an expired schedule fails falsely.

Apply the shared sunset deadlines (import them from sunsets.py, do not copy the constants) to the history windows, so runs are required before a workflow's sunset and not after it.

## Read first
AGENTS.md, tools/check_workflow_history.py, pipeline/sunsets.py, tests/test_harden.py, runbook files that cite `check_workflow_history --days`.

## Constraints
- Keep fail-closed behaviour: a workflow whose guard cannot be recognised stays strict.
- Do not edit tests on main at origin/main except where one pins hourly required after its sunset; name any moved assertion in last.md.
- Do not touch files of open PRs: bin/night-watchdog, bin/tick, pipeline/night_start.py, pipeline/night_boundary.py, pipeline/fetch.py, tools/official_capture.py, runbook/night.md, .github/workflows/nz-election-night-rehearsal.yml.
- Commit in the worktree; do not push.

## Done
- Executable interval and history cases for each of hourly, daily, social: missing runs before the sunset fail, no runs after it pass, the interval straddling it requires only the part before. Each new case fails on origin/main and passes on HEAD.
- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` all passed.
- `bin/lint` ok.
- last.md: commit sha, output tail, moved assertions.
