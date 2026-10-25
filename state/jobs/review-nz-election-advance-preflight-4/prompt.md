Fourth fresh-context review of PR #84 (nz-election-advance-preflight), read-only. Worktree .worktrees/nz-election-advance-preflight,
branch change/nz-election-advance-preflight, head 4898e75 on main f5becd4. Fix round diff: git diff d540336..4898e75; full
diff: git diff f5becd4...4898e75. Judge against REVIEW.md; read product/nz_election/runbook/advance.md.

The third review asked: cli() sanitizes every unexpected exception, not only OSError/ValueError (RuntimeError, KeyError,
TypeError text escaped at advance_preflight.py:85-92). Check that no exception text or capture content reaches stdout or
stderr on any path, that MISSING_EVIDENCE, KeyboardInterrupt and SystemExit behave as before, that the earlier items
(explicit daily/cumulative evidence, shared CSV reader rejects malformed quoting before filtering, supersession runbook,
no raw header in diagnostics) still hold, and that no test on main at f5becd4 was weakened.
Supervisor host run on 4898e75: test_advance*.py 128 passed; 4 fail with advance_preflight.py at d540336; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
