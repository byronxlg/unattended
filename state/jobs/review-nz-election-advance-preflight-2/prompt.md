Second fresh-context review of PR #84 (nz-election-advance-preflight), read-only. Worktree .worktrees/nz-election-advance-preflight,
branch change/nz-election-advance-preflight, head 7192300 on main f5becd4. Fix round diff: git diff 3c427e6..7192300; full
diff: git diff f5becd4...7192300. Judge against REVIEW.md; read product/nz_election/runbook/advance.md.

The first review asked for: (1) the preflight must not guess daily vs cumulative: it requires explicit header evidence
and fails otherwise; (2) malformed quoting is rejected by the one shared CSV reader before any rows or columns are
filtered, in both the preflight and the pipeline; (3) the runbook documents how a reviewed shorter-but-corrected capture
supersedes an earlier one without deleting captures. Check all three hold, that error messages never echo raw file
content, and that no test on main at f5becd4 was weakened.
Supervisor host run on 7192300: test_advance.py 108 passed; 8 fail with the code at 3c427e6; verify.py advance PASS; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
