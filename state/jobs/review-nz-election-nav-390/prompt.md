Fresh-context review of PR #108 (nz-election-nav-390), read-only. Worktree .worktrees/nz-election-nav-390, branch
change/nz-election-nav-390, head df01417, stacked on change/nz-election-parties-credit (fa33005).
Diff: git diff fa33005...HEAD. Judge against REVIEW.md. Brief: state/jobs/nz-election-nav-390/prompt.md and
state/jobs/nz-election-nav-390-fix-1/prompt.md; design product/nz_election/DESIGN.md.

Check: header nav is one row at 360 and 390 on every route, every link reachable by keyboard and touch (44 px targets),
a focused link is fully visible (the scroll padding works in the header scroller, not only the page), the current page
is marked, nothing scrolls the page sideways; 1280 unchanged; no type below the 16 px reading floor; tests check
behaviour, not markup or class names. Supervisor host evidence: pytest -k "design or home or nav or header" 166 passed
incl. Chromium; origin/data build PASS 82 routes; screenshots /tmp/sh-nav/home-360.png, home-390.png, home-1280.png.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line, and the three weakest
visual points. You cannot approve.
