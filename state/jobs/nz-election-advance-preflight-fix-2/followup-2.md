Follow-up 2 on PR #84 (nz-election-advance-preflight), same worktree and branch, head 7192300. Second fresh review
requested one change:

1. product/nz_election/tools/advance_preflight.py:49: the missing-evidence error echoes the raw count header via
   repr(column), and the CLI prints it (line 90). Diagnostics must not carry input file content.

Invariant: no error or log line from the preflight or the advance consumers prints a value read from the capture
(header text, cell values); they name the check and, where useful, a structural position (column index, row number).
Apply it to every error path in advance_preflight.py and the advance parser it calls, not only line 49. The accepted
record's kind_inference field (line 66) is output data, not a diagnostic; leave it.

Tests: the branch's own tests (added since main at 3c427e6's base) move with it, including the one that expects the
header in the message; tests on main at the base sha stay untouched. Add a regression with a marker string in a header
that asserts the marker is absent from stderr and the exception text, failing on 7192300.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py` passes, the regression fails on
7192300, `bin/lint` prints lint ok. Commit in the worktree, do not push, do not commit last.md.
