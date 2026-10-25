Follow-up 3 on PR #84 (nz-election-advance-preflight), same worktree and branch, head d540336. Third fresh review
requested one change:

1. product/nz_election/tools/advance_preflight.py:85-92: cli() sanitizes only OSError and ValueError. A RuntimeError,
   KeyError or TypeError raised under inspect() escapes with its text (and a traceback) on stderr, so capture content
   can still reach the terminal or an Actions log.

Invariant: nothing the CLI prints on failure carries text from an exception or from the capture; any unexpected
exception at the CLI boundary exits nonzero with the fixed advance.ERROR message (MISSING_EVIDENCE keeps its own code).
Do not catch BaseException subclasses that are not Exception (KeyboardInterrupt, SystemExit from argparse).

Tests: the branch's own tests move with it; tests on main at the base sha stay untouched. Add a regression that injects
RuntimeError, KeyError and TypeError carrying a marker string from inspect() and asserts the marker is absent from
stdout, stderr and the SystemExit text, failing on d540336.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py` passes, the regression fails on
d540336, `bin/lint` prints lint ok. Commit in the worktree, do not push, do not commit last.md.
