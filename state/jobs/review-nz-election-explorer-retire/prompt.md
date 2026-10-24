Fresh-context review of PR #74 (nz-election-explorer-retire), read-only. Worktree .worktrees/nz-election-explorer-retire,
branch change/nz-election-explorer-retire, head ff4aaab. Diff: git diff 31b71cb...ff4aaab -- product. Judge against REVIEW.md.

Context: retires the coalition explorer client (web/coalitions.mjs and its browser test, runner, renderer). No route
has rendered it since 170bf94. Check: no built route or stage copy references coalitions.mjs; the allocator still ships
if any route loads it; every old polls/ fragment alias still resolves (polls_page.py aliases, BROKEN_FRAGMENT);
each retired verify/home_checks/landmark_checks check has a replacement invariant that would catch the same class of
regression on the current page, not a weaker one; tests that pin server output (strip, TOP labels, majority) are not
weakened; SCRIPT_ALLOWLIST narrowed rather than widened. No data family, workflow or page copy changes.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
