Second fresh-context review of PR #61 (nz-election-parties-page), read-only. Worktree .worktrees/nz-election-parties-page,
branch change/nz-election-parties-page, head 367556d. Fix rounds: git diff b389f5e..367556d; whole change:
git diff main...367556d. Judge against REVIEW.md (question test first), intent/nz-election/pages/parties.md and the
first review's findings (gh pr view 61 --comments).

Check: (1) picker chips stay on one row at 360 and 390 with a test, (2) snapshot provenance validators in
snapshots.py reject malformed records (missing source, bad URL, bad licence) with tests, (3) the heading outline on
parties/ is h1 then h2 with no skipped level, and the new browserless outline test covers all 81 routes and fails on
bbbb576, (4) nothing on home or polls changed beyond party links, (5) no check on main weakened.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
