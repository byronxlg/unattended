Fresh-context review of nz-election-home-defects, read-only. Worktree .worktrees/nz-election-home-defects,
branch change/nz-election-home-defects, head 938df4f on main 4dbb18e. PR #38 (`gh pr view 38 --comments`).
Diff: git diff 4dbb18e..938df4f. Judge against REVIEW.md, intent/nz-election/design-principles.md and the
brief state/jobs/nz-election-home-defects/prompt.md (main checkout). The engineer's account
(state/jobs/nz-election-home-defects/last.md) is a claim to check.

Host harness screenshots on 48b05aa: .worktrees/nz-election-home-defects/artifacts/review/shots/
(home-360x780, home-390x844, home-1280x800); a 390 full-page crop of the modules is at /tmp/home-mods.png.

Check: (1) each of defects 5, 6, 7, 8, 9, 11 is fixed at its cause, not its text; (2) the latest polls
party selection is right for parties with an electorate win but under 5%, and for missing shares;
(3) market questions are faithful to the contract (no invented proposition; closed contracts flagged);
(4) no test on main at 4dbb18e weakened beyond the one named move, no harness check loosened;
(5) every number keeps its provenance link.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
