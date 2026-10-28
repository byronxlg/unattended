Fresh-context review of PR #118 (nz-election-advance-acceptance), read-only. Worktree .worktrees/nz-election-advance-acceptance,
branch change/nz-election-advance-acceptance, base origin/main. Diff: git diff origin/main...HEAD -- product/ runbook/.
Judge against REVIEW.md.

Goal: an opt-in check, `verify.py advance --require advance`, that fails when the newest registered 2026 advance capture is
not what the bundle publishes (date and cumulative count) or not what home and vote/ visibly say. Every failure a named code
and nonzero; no upstream text in errors; default verify unchanged; tests check behaviour, not markup.

Fourth review (after fix-3 fb1df65): the third review found the count matched as a suffix (advance_acceptance.py:96), so
"-175,748" or "1.175,748" passed. fix-3 requires a complete count token; attached signs and decimal prefixes now give
ADVANCE_RENDER_MISMATCH on both routes (supervisor host: test_advance* test_verify* 315 passed; 10 new cases fail at 20b6792).
Check the fix and review the full diff. The page renderer formats the count itself, so only report a further token-format
case as Important if the site's own renderer could produce it.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
