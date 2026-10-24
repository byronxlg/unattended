Fresh-context review of PR #77 (nz-election-harden), read-only. Worktree .worktrees/nz-election-harden, branch
change/nz-election-harden, head 5835b0e. Diff: git diff f406321...5835b0e. Judge against REVIEW.md.

Context: adds bin/nz-election-harden (product/nz_election/tools/harden.py): runs every evals/*/check.sh, verify.py all
on a bundle and site, and tools/check_workflow_history.py (per-day success/failure of the daily, hourly and social
daily workflows from the GitHub API), naming the first failure; --offline skips network evals and history as SKIP,
which fails the gate. Tests with an injected runner, runbook section. This is the phase 5 "all evals green" gate.
Check: a SKIP or a missing eval can never read as PASS; an eval's nonzero exit, a verifier FAIL line, or a missing
workflow day fails; the history rule (a day with one success and one failure passes) is right or should be stricter
for the hourly (18 runs a day observed, 24 scheduled); no secret or token is printed; nothing weakens an existing check.
Host: test_harden.py 53 passed; check_workflow_history.py --days 3 PASS. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
