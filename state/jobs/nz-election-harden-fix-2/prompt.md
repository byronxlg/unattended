# Fix round 2 for PR #77 (harden gate)

The second fresh review requested changes, one Important, and it is the supervisor's policy wording
in fix-1 that allowed it ("from the day start and to the day end"). This is a fix job on
change/nz-election-harden: tests on main at the base sha f406321 do not change; tests this branch
added (test_harden.py and check_workflow_history tests) move with the fix. Nothing weakens a check.

1. `product/nz_election/tools/check_workflow_history.py:53` `day_result`: midnight splits a real gap.
   Hourly successes at 03:00, 06:00, ..., 21:00 NZ on three days pass, though the overnight gap is
   six hours. Measure the gap between consecutive successes across day boundaries: for each day,
   the boundaries are the last success before the day (if any run exists in the window before it)
   and the first success after it (or the day end when the day is today or the window ends). The
   first day of the window with no earlier data may use the day start. Update the runbook and the
   tool's help text to say gaps are measured across midnight.

Definition of done (paste each output in last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes, with a regression
  test for the three-day 03:00-21:00 case that fails on a67a6fa (say so with the output).
- `bin/lint` prints ok.
- Commit on the branch, do not push. Do not commit last.md.
