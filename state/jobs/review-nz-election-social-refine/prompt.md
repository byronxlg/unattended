Fresh-context review of nz-election-social-refine, read-only. Worktree .worktrees/nz-election-social-refine,
branch change/nz-election-social-refine, head ff598b4 on main. PR #56 body (`gh pr view 56`) is a claim to check.
Diff: git diff main...ff598b4. Judge against REVIEW.md and the brief state/jobs/nz-election-social-refine/prompt.md
(main checkout).

Check: (1) a run on an already-spent NZ budget day makes no network request, appends no ledger row, leaves
social/credits and social/daily byte-identical, publishes a status row, and exits 0; (2) a cap reached during
collection, and a run with a reservation (the reserve/collect split in .github/workflows/nz-election-social-daily.yml),
still behave as on main: trace the workflow steps for the new 'budget-spent' result (outputs, validated=true,
publish step) and say whether anything downstream misreads it; (3) the budget_spent arithmetic is right at the
boundary (CAP minus reserved equal to RESERVATION) and across NZ midnight; (4) the status message reads correctly
with and without prior data, no "no previous data" phrase left; (5) the s197 freeze path is unchanged; (6) no test
on main weakened, verify.py's changed assertion is at least as strong; (7) runbook true.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
