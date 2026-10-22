Fresh-context review of PR #63 (nz-election-social-model), read-only. Worktree .worktrees/nz-election-social-model,
branch change/nz-election-social-model, head 1e53a1e. Diff: git diff main...1e53a1e. Judge against REVIEW.md.

Context: the 2026-10-22 social daily failed because Jev rotated jev-latest to jev-1.14.0 while validation accepts only
jev-1.13.0. The change sends the pinned MODEL_VERSION in requests. Check: the request and the validator cannot drift
apart again; the eval evals/social-model-rotation fails on main and passes here; the regression test exercises the
real request path (injected transport), not a mock that bypasses it; the runbook says how to move the pin; no check on
main weakened; nothing in data/, logs or the PR leaks raw posts, handles or keys.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
