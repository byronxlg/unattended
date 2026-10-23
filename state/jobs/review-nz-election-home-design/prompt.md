Fresh-context design review of nz-election-home-design, read-only. Worktree .worktrees/nz-election-home-design,
branch change/nz-election-home-design, head 58a08dd on main 6e5f3bf. PR #39 (`gh pr view 39 --comments`).
Diff: git diff 6e5f3bf..58a08dd. Judge against REVIEW.md, intent/nz-election/design-principles.md, the brief
state/jobs/nz-election-home-design/prompt.md and followup-1.md (main checkout). The engineer's account
(state/jobs/nz-election-home-design-fix-1/last.md) is a claim to check.

Host Chromium full-page home screenshots of 58a08dd under /unattended: .worktrees/nz-election-home-design/artifacts/home-design/
fu-360.png, fu-390.png, fu-1280.png (crops fu-1280-0..3.png, fu-390-0..2.png). Look at them; judge them against
the 538 2024 forecast style the principles describe (one answer up top, a graphic per module, restrained colour).

Check: (1) the hero sentence and the 64/67 explanation are derived from the seat numbers for the above, equal and
below cases, never hard-coded; (2) every chart has an accessible equivalent (hidden table or aria) with exact values
and keeps its provenance link; (3) HOME_CHART_TEXT_SIZE measures real rendered glyph size and would fail on SVG text
that scales; (4) no test on main at 6e5f3bf weakened beyond contracts the brief names as moving, no harness check
loosened; (5) layout holds at 360 with no horizontal overflow.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
