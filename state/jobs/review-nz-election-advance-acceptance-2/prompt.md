Fresh-context review of PR #118 (nz-election-advance-acceptance), read-only. Worktree .worktrees/nz-election-advance-acceptance,
branch change/nz-election-advance-acceptance, base origin/main. Diff: git diff origin/main...HEAD -- product/ runbook/
(pipeline/advance_acceptance.py, pipeline/verify.py, tools/harden.py, tests/test_advance_acceptance.py, runbook/nz-election.md).
Judge against REVIEW.md.

Goal: an opt-in check, `verify.py advance --require advance`, that fails when the newest registered 2026 advance capture is
not what the bundle publishes (date and cumulative count) or not what home and vote/ say. Check: every failure is a named code
and nonzero; no upstream text in errors; ADVANCE_GAP never lets a zero-filled cumulative count through; default verify
behaviour (without --require advance) is unchanged; the runbook commands match the CLI; tests check behaviour, not markup.
Supervisor host evidence: pytest test_advance*.py test_verify*.py test_harden*.py 492 passed after merging main; on the real
origin/data bundle (no advance family yet, the daily has not run since #114) it prints FAIL advance: ADVANCE_NOT_PUBLISHED rc 1.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.

Second review (PR #118 after fix-1 65fbef1): the first review found advance_acceptance.py VisibleText accepted CSS-hidden text. fix-1 excludes inline-hidden elements and descendants so a hidden count sentence returns ADVANCE_NOT_PUBLISHED, with both-route regressions (supervisor host: test_advance* 210 passed; 28 fail with advance_acceptance.py at 2f93e28). Check the fix (other hiding methods the site's own markup uses?) and that nothing else regressed; review the full diff against origin/main.
