Third fresh-context review of PR #84 (nz-election-advance-preflight), read-only. Worktree .worktrees/nz-election-advance-preflight,
branch change/nz-election-advance-preflight, head d540336 on main f5becd4. Fix round diff: git diff 7192300..d540336; full
diff: git diff f5becd4...d540336. Judge against REVIEW.md; read product/nz_election/runbook/advance.md.

The second review asked: no error path in tools/advance_preflight.py echoes raw header or file content (it found one at
advance_preflight.py:49). Check every diagnostic in the preflight and the CLI boundary uses fixed or structural messages,
that unexpected exceptions do not forward their text, that the earlier three items (explicit daily/cumulative evidence,
shared CSV reader rejects malformed quoting before filtering, supersession runbook) still hold, and that no test on main
at f5becd4 was weakened.
Supervisor host run on d540336: test_advance*.py 122 passed; 4 fail with advance_preflight.py at 7192300; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
