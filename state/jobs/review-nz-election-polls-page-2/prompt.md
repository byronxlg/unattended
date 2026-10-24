Fresh-context review of PR #71 (nz-election-polls-page), read-only. Worktree .worktrees/nz-election-polls-page,
branch change/nz-election-polls-page, head 280b2c2. Diff: git diff 382c962...280b2c2 -- product. Judge against REVIEW.md,
question test (pass 4) first, against the accepted page plan intent/nz-election/pages/polls.md.

Context: a build job (not a fix job), so test contracts for the old polls layout may move with the page; check that no
other route's assertion, byte or font budget, or allocator threshold was weakened (the report says none). Check the
101 legacy fragment ids are preserved, the threshold sentence boundaries (3 to 7 percent inclusive), the ten-newest
ordering, omission when a block's data is absent (no "not available" text), and the seat helper's majority with
overhang (live 132 or 133 seats, 67 needed). Screenshots from the host are at /tmp/polls-page/polls-390.png and
/tmp/polls-page/polls-1280-full.png if readable; the supervisor already noted label leader lines that read as data and
a double period in the Wikipedia caption.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.

Second review round. The branch head is now 93696cc on change/nz-election-polls-page (fix-1 on top of 280b2c2). Check that each Important finding from the first review is resolved and that fix-1 introduced nothing new: neutral trend-label ticks, duplicate punctuation, the leading-party change summary, the night/ hydration fix (night_hydration.mjs and the startup modules), the strengthened fold check in screenshots.py (it must not be weaker than before; the JS/no-JS equality stays exact), and test_polls_fix1.py exercising real chart output. Pre-existing tests on main at 8a8d484 are protected; this branch's own tests may move. Report findings per REVIEW.md with a verdict line: accept or request changes.
