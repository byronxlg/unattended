Fresh-context review of PR #67 (nz-election-electorate-page), read-only. Worktree .worktrees/nz-election-electorate-page,
branch change/nz-election-electorate-page, head 1df8249. Whole change: git diff origin/main...1df8249. Judge against REVIEW.md (question
test first), intent/nz-election/pages/electorate.md (the accepted page plan: questions in rank order, page order, not shown)
and the brief state/jobs/nz-election-electorate-page/prompt.md.

Check: (1) rendered order on a general seat, a Maori seat and Port Waikato follows the plan's question rank, (2) candidate
names, parties and incumbent flags come only from the reconciliation snapshot, never inferred, (3) the locator SVG has
provenance and a licence and its byte cap is enforced by a check, (4) the seven replaced old-layout assertions in route_checks.py,
screenshots.py and the electorate tests: each replacement is at least as strict for what remains on the page; no check on main
weakened beyond the removed modules, (5) absent data renders as absent (no "not available" text), (6) no per-page byte or
transfer budget raised.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
