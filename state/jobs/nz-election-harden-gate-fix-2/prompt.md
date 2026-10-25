Follow-up 2 on PR #83 (nz-election-harden-gate), same worktree and branch, head 9c5c5fc. Second fresh review requested changes:

1. product/nz_election/tools/check_workflow_history.py:179: after shlex removes quoting, a newline inside a quoted string
   becomes a command separator, so `echo '<newline> python3 product/nz_election/pipeline/night_live.py'` in a `run: |`
   block declares the night guard. Probe with empty history returned PASS. False pass.
2. check_workflow_history.py:174: comment stripping consumes the command-separating newline, so `set -e # setup` followed
   by a real `python3 .../night_live.py` line is not recognized (FAIL outside the night window). Backslash-continued
   invocations are also missed. False fail.

Invariant (unchanged from follow-up 1): the guard is declared only by a `run:` step whose shell commands actually invoke
the guard script; text inside quotes, echo arguments and comments never counts, and a real invocation after a comment
line, after `cmd # comment`, or split with a trailing backslash does count. Choose the shape (a small tokenizer that keeps
quote state across lines, or another approach); do not widen it into a full shell parser.

Tests: the branch's own tests in test_harden.py move with it; tests on main at dc57e78 stay untouched. Add a regression for
each of the three cases above (quoted newline, trailing comment then invocation, backslash continuation), each failing
on 9c5c5fc.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes, the new cases fail with
check_workflow_history.py at 9c5c5fc, `bin/lint` prints lint ok. Commit in the worktree, do not push, do not commit last.md.
