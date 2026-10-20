Second fresh-context review of nz-election-social-refine (PR #56), read-only. Worktree .worktrees/nz-election-social-refine,
branch change/nz-election-social-refine, head b5b0b9d. Diff: git diff main...b5b0b9d. The first review asked for one
Important: the spent-day status kept error_code SOCIAL_CREDIT_CAP, so publish.py (about lines 224-227) still failed
the reserve job. Fix b5b0b9d sets error_code null on the spent-day status. Judge against REVIEW.md.

Check: (1) the spent-day path now exits 0 end to end through the publish step of
.github/workflows/nz-election-social-daily.yml (trace it); (2) a cap reached mid-collection is still fatal with
SOCIAL_CREDIT_CAP; (3) nothing on the site or verify.py reads error_code null as "fresh data" (status message and
last-success timestamp preserved, stale data not shown as current); (4) no test on main at 6afc912 weakened (the
branch's own tests may move); (5) runbook true.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
