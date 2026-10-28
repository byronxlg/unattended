# Follow-up 1: history-sunsets (PR #125)

Fresh review, confirmed by the supervisor at `product/nz_election/tools/check_workflow_history.py:396`:
recovery evidence uses `end <= stamp <= query_end`, so when `query_end` is the collection sunset a
success created exactly at the sunset counts as recovery for a failure one second before it. A run
at or after the sunset is outside the window and must not be evidence.

Do:
1. Exclude the sunset instant from recovery evidence (a success at the sunset or later does not
   recover a gap). Do not change behaviour for windows that do not end at a sunset.
2. Add checker tests through the real `main` with the injected clock and runner: a failure at
   sunset minus 1 s with a recovery success at sunset minus 1 s (passes only if coverage allows),
   at the sunset (must not recover), and at sunset plus 1 s (must not recover).

Ignore the review's second item (state files, journal, prompts): those are the reviewer diffing
against a newer main; the PR diff touches only product files and the runbook. Do not touch state/.

Constraints: tests on main at the base sha are unchanged; this branch's own tests may move.
Commit in the worktree, do not push.

Done: `uv run --with pytest pytest -q product/nz_election/tests/test_workflow_history_sunsets.py product/nz_election/tests/ -k 'harden or history or sunset'` passes; the new at-sunset case fails with check_workflow_history.py at 498932c.
