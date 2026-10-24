# Fix round 1 for PR #77 (harden gate)

The fresh review of PR #77 requested changes. Fix all four Important items on this branch
(change/nz-election-harden, worktree .worktrees/nz-election-harden). This is a fix job: tests on
main at the base sha f406321 do not change; tests this branch added (test_harden.py and any
check_workflow_history tests) move with the fix. Nothing weakens an existing check.

1. `product/nz_election/tools/harden.py:65` discovery: a missing eval silently drops out (removing
   `evals/social-retry-budget/check.sh` still gives PASS with seven evals). Check discovery against a
   required inventory (a committed list, or every directory under `evals/` must have its check), and
   fail naming the missing eval.
2. `harden.py:57` eval output: an eval printing `SKIP ...` or `FAIL ...` with exit 0 counts as PASS.
   Treat any SKIP or FAIL result line as a failure of the gate, naming the eval.
3. `harden.py:86`: without `--history` the gate prints the same `PASS harden`. Milestone PASS requires
   the history check; without it print a distinct result (for example `PARTIAL harden (history not
   checked)`) and exit nonzero, or require an explicit `--local` flag that prints PARTIAL.
4. `tools/check_workflow_history.py:60`: one success plus 23 failures in a day passes. Policy the
   supervisor accepts (state it in the runbook and the tool's help):
   - hourly workflow: a day passes when the gap between consecutive successful runs (and from the day
     start and to the day end) is never more than 3 hours, and every failure is followed by a success
     within 2 hours. GitHub drops scheduled runs, so the run count itself is reported, not required.
   - daily workflows: a day passes when its last run of the day concluded success (a failure followed
     by a successful rerun the same day is a recovery, reported as such).
   - Print per workflow per day the counts and the reason for any FAIL.

Definition of done (run each, paste the output in last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes, with new tests for
  each of the four false-PASS paths that fail on 5835b0e.
- `bin/lint` prints ok.
- Commit on the branch, do not push. Do not commit last.md.
