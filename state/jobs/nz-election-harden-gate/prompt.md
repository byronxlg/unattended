# Build: the harden acceptance gate must not fail a healthy history or an expected omission

Change: nz-election (schedule.md "4 Nov: harden"; readiness audit research-nz-election-readiness, item 1).
Read first: `AGENTS.md`, `intent/nz-election/schedule.md`, `product/nz_election/tools/check_workflow_history.py`,
`product/nz_election/tools/harden.py`, `evals/pages-verify-polls-only/check.sh`, `product/nz_election/tests/test_harden.py`,
the workflow files under `.github/workflows/` (read only, do not edit them; an open PR changes them).

## Problem
1. `check_workflow_history.py` classifies every non-hourly schedule as daily (`hourly_workflow`), so the
   election-night workflow, whose cron only fires from 7 November, is required to have runs on 1 to 3
   November. A healthy injected history fails the gate.
2. `harden.py` rejects any `SKIP` line from `verify.py all`, while the polls-only eval expects
   `SKIP night/waterfall` on a bundle without a night family. One of the two is wrong for each context.

## Goal
1. The history check derives each workflow's expected cadence and active window from its cron
   (hourly, daily, or a dated/annual schedule that only fires on given days) and from any active-window
   guard the workflow declares; it requires runs only on days the schedule fires. A real missing run on
   a day the schedule fires still fails, with the same reason text as today.
2. `harden.py` accepts `SKIP` for families that are optional in the context it checks (pre-night
   bundle) and fails on them when told the release is the election-night acceptance: reuse
   `verify.py all --require` (merged in fd885f4) rather than a second list. Mandatory night/waterfall
   checks for release acceptance stay mandatory.
3. The polls-only eval and harden agree; nothing weaker: no check is removed, only scoped.

## Constraints
Tests on main at the base sha are protected except the ones that pin the wrong cadence rule; if one
must move, say which and why in your summary. No workflow file edits. No network.

## Done
- New tests in `test_harden.py` (or a new `test_workflow_history.py`): annual/dated schedule with a
  healthy history passes; the same schedule with a missing run on a firing day fails; daily schedule
  with a missing day fails; pre-night bundle with SKIP night passes harden; release mode with SKIP night fails.
  At least one new test fails on the base sha (say which).
- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes; `bash evals/pages-verify-polls-only/check.sh` PASS; `bin/lint` ok.
- Commit in the worktree; summary lists files, tests, and the command output lines.
