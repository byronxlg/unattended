Fresh-context review of nz-election-principles, read-only. Worktree .worktrees/nz-election-principles,
branch change/nz-election-principles, head 215baf9 on main b0f3b3f. PR #36 (`gh pr view 36 --comments`).
Diff: git diff b0f3b3f..215baf9. Judge against REVIEW.md and intent/nz-election/design-principles.md
(issue #34: colour, layout, no collapsibles on the home, references moved off the main page).
The engineer's accounts (state/jobs/nz-election-principles*/last.md in the main checkout) are claims to check.

Host harness screenshots on 215baf9: .worktrees/nz-election-principles/artifacts/nz-election/screenshots/
(look at home-360x780, home-390x844, home-1280x800, home-390-dark, downloads-360x780, polls, an electorate, night).

Check: (1) the home and the restyled routes follow each principle in design-principles.md, and the
screenshots show it; (2) every number on the home still reaches its provenance (methods/sources link
works, no figure without a source path); (3) no test on main at b0f3b3f weakened, screenshots.py
unchanged, no check moved; (4) nothing regressed on routes the change did not mean to touch
(fragments preserved on polls/, social POC label, accessibility of the hero and seat bar).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
