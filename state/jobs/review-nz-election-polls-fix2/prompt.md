Fresh-context review of nz-election-polls-fix2, read-only. Worktree .worktrees/nz-election-polls-fix2,
branch change/nz-election-polls-fix2, head 03a72cf on main fe698de. PR #46. Diff: git diff fe698de..03a72cf.
Judge against REVIEW.md. Briefs: state/jobs/nz-election-polls-fix2/prompt.md and followup-1.md (main
checkout); the engineer's account state/jobs/nz-election-polls-fix2-fix-1/last.md is a claim to check.

Check: (1) a release-date sort value on a poll row is accepted only within a bound and dates outside it
still raise invalid_dates; (2) public status, log and summary carry only structural locators, no raw
wikitext (the PR #27 rule); (3) the six exception tests on main that moved assert the same or a stronger
invariant, nothing weakened beyond what followup-1 authorizes; (4) the eval evals/polls-release-date-sort
fails on main and passes here.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
