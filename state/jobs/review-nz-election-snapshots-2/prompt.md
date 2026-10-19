Second fresh-context review of nz-election-snapshots, read-only. Worktree .worktrees/nz-election-snapshots,
branch change/nz-election-snapshots, head 281e7d8 (fix-1) on c737231; PR #42 (`gh pr view 42 --comments`).
The first review (state/jobs/review-nz-election-snapshots/last.md in the main checkout) asked for one Important:
record licences validated. Diff to judge: git diff c737231..281e7d8, plus anything in 05b311b..281e7d8 the fix
touched. Against REVIEW.md.

Check: (1) the Important is resolved: an unknown or missing record licence raises naming file and record, and
the new tests fail on c737231; (2) no test on main (05b311b) weakened; (3) nothing else regressed in the loader.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
