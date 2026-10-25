# Follow-up 1 on PR #83 (harden gate): fresh review request changes

Fix job on your own branch `change/nz-election-harden-gate`. Tests on `main` at the base sha are
protected: do not weaken or edit them. Tests this branch added move with it. Commit in the worktree,
do not push.

Two Important findings from the fresh review (full text on PR #83):

1. `product/nz_election/tools/check_workflow_history.py:129`: cadence combines hours from all
   `schedule` crons ignoring their month/day/weekday restrictions. Example: hourly `17 * * 7 *` plus
   daily `0 0 * 11 *` makes a healthy November day fail with "success gap 11 hours exceeds 3 hours";
   `0 0-10 * * *` passes with only its last run, hiding ten missing runs. Invariant: for each
   evaluated date, the expected runs and the allowed gap come only from the crons whose fields match
   that date (and the gap is measured inside the active interval, not only after the last fire).
2. `check_workflow_history.py:114`: guard detection matches any text, so a comment
   `# See product/nz_election/pipeline/night_live.py` exempts a workflow from history checks.
   Invariant: only an actual guarded execution step counts (a `run:` command that invokes the guard),
   never comments or incidental mentions.

Definition of done:
- A regression test per finding that fails on d891756 and passes on HEAD (say so in last.md with
  the failing output).
- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes.
- `bin/lint` prints `lint ok`.
- last.md: what changed, the commands and their output.
