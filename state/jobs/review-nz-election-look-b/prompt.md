Fresh-context design review of nz-election-look-b, read-only. Worktree .worktrees/nz-election-look-b,
branch change/nz-election-look-b, head 11c0421 on main 4987a93. PR #45 (`gh pr view 45 --comments`).
Diff: git diff 4987a93..11c0421. Judge against REVIEW.md, intent/nz-election/design-principles.md,
intent/nz-election/look-538.md, the briefs state/jobs/nz-election-look-b/prompt.md and
state/jobs/nz-election-look-b-fix-1/prompt.md (main checkout). The engineer's account
(state/jobs/nz-election-look-b-fix-1/last.md) is a claim to check.

Host Chromium screenshots of 11c0421 (populated synthetic build): /tmp/lookb-shots/ (home-1280x800.png,
home-390x844.png, home-360x780.png, electorates--*-390x844.png, others). Look at home 1280/390 and two
electorates; judge them against the 538 2024 forecast style (one answer up top, a graphic per module,
restrained colour) and issue #40 ("never show not available").

Check: (1) absent data is omitted, never rendered as "not available"/"unavailable"/placeholder, and a build
check enforces it; (2) every snapshot-derived value on a page carries its source and licence (portraits
credit), nothing from snapshots without provenance; (3) the tile map and every chart has an accessible
equivalent with exact values; (4) no test on main at 4987a93 weakened beyond contracts the briefs name as
moving, no harness check loosened; (5) layout holds at 360 with no horizontal overflow.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
