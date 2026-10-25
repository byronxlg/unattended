Fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head d891756 on main dc57e78. Full diff: git diff dc57e78...d891756. Judge against
REVIEW.md; read intent/nz-election/schedule.md ("4 Nov: harden") and product/nz_election/runbook/night.md.

Goal: (1) tools/check_workflow_history.py derives each workflow's expected cadence and active window from its cron
(hourly, daily, dated or annual schedules that fire only on given days) and any active-window guard the workflow
declares, and requires runs only on days the schedule fires; a real missing run on a firing day still fails with the
same reason text. (2) tools/harden.py accepts SKIP for families optional pre-night and, for election-night release
acceptance, reuses verify.py all --require night,waterfall (no second list). (3) evals/pages-verify-polls-only and harden
agree; no check removed, only scoped.

Look hard at: cron parsing edge cases (ranges, lists, steps, day-of-month plus month, day-of-week, UTC vs NZ day
boundaries), a workflow with no cron, whether a guard can make a workflow silently exempt forever, whether release mode
can be reached without --require, and whether any test on main at dc57e78 was weakened.
Supervisor host run on d891756: test_harden.py 120 passed; 21 of them fail with base tools; lint ok. Do not run pytest;
read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
