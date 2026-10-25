Fresh-context review of PR #84 (nz-election-advance-preflight), read-only. Worktree .worktrees/nz-election-advance-preflight,
branch change/nz-election-advance-preflight, head 3c427e6 on main f5becd4. Full diff: git diff f5becd4...3c427e6. Judge against
REVIEW.md; read product/nz_election/runbook/advance.md and intent/nz-election/schedule.md.

Goal: (1) tools/advance_preflight.py validates an operator-captured EC advance voting file before it is committed and
prints a review draft; acquisition time is operator input, never inferred. (2) advance.py rejects a replacement capture
shorter than the one it replaces (SHORTER_ADVANCE_CAPTURE). (3) verify.py advance --require-year 2026 fails
MISSING_ADVANCE_CAPTURE until a 2026 capture exists; without the flag behaviour is unchanged.

Look hard at: malformed CSV (quoting, BOM, blank rows, duplicate dates, non-monotonic cumulative totals, daily vs
cumulative confusion), whether the preflight and the pipeline share one parser (no second set of rules), whether an
error message can echo raw file content, whether a shorter-but-corrected capture has a documented path, and whether any
test on main at f5becd4 was weakened.
Supervisor host run: test_advance.py 97 passed; 6 fail with advance.py at dc57e78; lint ok. Do not run pytest; read and
probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
