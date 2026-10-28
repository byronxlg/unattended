Fresh-context review of the nav-legend PR (change/nz-election-nav-legend), read-only. Worktree .worktrees/nz-election-nav-legend,
base origin/main. Diff: git diff origin/main...HEAD -- product/. Judge against REVIEW.md and product/nz_election/DESIGN.md.

Goal: at 360/390 the header nav shows only whole labels and the current route is visible on every page; home seat
legend grouped by bloc. Check: the inline handler is allowed by the site's script policy and degrades with JS off
(every link still reachable by scroll and keyboard; nothing hidden from assistive tech or focus wrongly); no layout
shift or resize bug (rotate 390 to 844, desktop unchanged); tests check geometry and behaviour, not markup or class names.
Supervisor host evidence: pytest -k "design or home or header or nav" 163 passed incl. Chromium; headers at
360/390/1280 on home, electorates/, night/ measured and looked at.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
