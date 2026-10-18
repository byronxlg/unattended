Fresh-context review of increment 7 (markets and daily automation), read-only. Worktree
.worktrees/nz-election-7, branch change/nz-election-7, two commits on top of main 29bf079
(git diff main...HEAD; 37e3b9d captures, 176944f build). PR #30 (`gh pr view 30 --comments`)
carries the supervisor's review (request changes on the home markets module: height, placeholder
rows, raw floats); do not repeat those, look for what they miss. Intent and plan:
intent/nz-election/plan-m2.md (increment 7, "Markets", "Daily refresh, publication and Pages",
supervisor decisions 5, 6, 8, 9, 10), spec.md requirement 5, intent/nz-election/home.md (markets
placement). The engineer's account is state/jobs/nz-election-7/last.md on main: claims to check,
not evidence. Judge against REVIEW.md.

Check, in this order:
(1) success_order treats a missing fetched_at as empty (the brief required it).
(2) nz-election-daily.yml: permissions, concurrency with the hourly and the social daily on the
data branch, the s197 freeze, the Pages trigger, bounded transport to Gamma (allowed host,
response cap, retries), failure leaves last-good data and a status row.
(3) Licence line exact ("Source: Polymarket. Subject to Polymarket terms. No open licence
asserted."), observation time beside prices, stale last-good prices keep their original time.
(4) Tests that moved (test_contracts.py, test_workflows.py): each moved because the registered
set moved, nothing weaker than main.
(5) Normalization: prices as probabilities, closed or resolved markets, missing fields.

Output: a verdict (accept, or request changes), then findings as Important or Nit, each with
file:line, what is wrong, the invariant, and how you would verify a fix. No code.
