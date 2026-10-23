Second fresh-context design review of nz-election-home-design, read-only. Worktree .worktrees/nz-election-home-design,
branch change/nz-election-home-design, head b6563b0 on main 6e5f3bf. PR #39 (`gh pr view 39 --comments`).
Focus diff: git diff 58a08dd..b6563b0 (fix-2); the whole change is git diff 6e5f3bf..b6563b0. Judge against REVIEW.md,
intent/nz-election/design-principles.md and state/jobs/nz-election-home-design-fix-2/prompt.md (main checkout),
which carries the first review's findings. The engineer's account (state/jobs/nz-election-home-design-fix-2/last.md)
is a claim to check.

Host Chromium screenshots of b6563b0 under /unattended: .worktrees/nz-election-home-design/artifacts/home-design/host-fix2/
full-1280.png, full-360.png (full page) and home-*.png (harness). Host harness PASS 79 routes 296 images, poll markers at
360 measured ratio 1.00.

Check: (1) the first review's Important is fixed: no trend line or connector implies data across a period a series was
not observed; a stale series ends at its own last point with its date; (2) the regression test for it would fail on
58a08dd; (3) pollster markers keep their shape at 360; trend dates align with the plotted interval; (4) no test on main
at 6e5f3bf weakened and no harness check loosened; (5) accessible equivalents and provenance links kept.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
