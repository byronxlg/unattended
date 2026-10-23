Fresh-context review of PR #66 (nz-election-parties-refine), read-only. Worktree .worktrees/nz-election-parties-refine,
branch change/nz-election-parties-refine, head e64ad5e. Whole change: git diff main...e64ad5e. Judge against REVIEW.md (question
test first), intent/nz-election/pages/parties.md and the brief state/jobs/nz-election-parties-refine/prompt.md.

Check: (1) each party snapshot type rejects a recognised-but-wrong licence and a missing source_url, with tests that fail on
729f9e7, (2) the committed snapshot records still load, (3) no credit caption on rendered parties/ starts with ". " or has an
empty side of " / ", tested on rendered HTML, (4) no check on main weakened (the removed RECORD_LICENCES line in
snapshots.py), (5) page order and content unchanged.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
