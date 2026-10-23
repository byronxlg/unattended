Second fresh-context review of nz-election-vote-facts, read-only. Worktree .worktrees/nz-election-vote-facts,
branch change/nz-election-vote-facts, head 9731f12 (fix-1) on eda2d3b, main d55b42e. PR #53 (`gh pr view 53`,
including the first review's Important item: offset +12:60 accepted at snapshots.py:251).
Diff of the fix: git diff eda2d3b..9731f12; whole change: git diff d55b42e..9731f12. Judge against REVIEW.md.

Check: (1) the offset check rejects out-of-range hours and minutes (+12:60, +15:00, -12:99) and still accepts
+13:00 and +12:00; (2) the regression tests fail without the fix; (3) no test on main at d55b42e weakened;
(4) nothing else in the change regressed.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
