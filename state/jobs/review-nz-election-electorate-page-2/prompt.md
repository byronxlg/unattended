Second fresh-context review of PR #67 (nz-election-electorate-page), read-only. Worktree .worktrees/nz-election-electorate-page,
branch change/nz-election-electorate-page, head b10fc2b. The fix round is git diff 1df8249..b10fc2b; the whole change is
git diff origin/main...b10fc2b. Judge against REVIEW.md (question test first), intent/nz-election/pages/electorate.md and
the first review's findings in state/jobs/review-nz-election-electorate-page/last.md.

Check: (1) each Important from the first review is fixed or was accepted with reasoning (incumbency source was accepted),
(2) the provenance line renders once per section, (3) candidate display names come from the reconciliation snapshot with a
deterministic display rule, not ad hoc casing that mangles Mc/Mac, hyphens or macrons, (4) the new regression test fails
on 1df8249's pipeline and passes on HEAD, (5) no check on main weakened, no budget raised.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
