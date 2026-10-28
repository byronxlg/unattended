Fresh-context review of PR #113 (nz-election-funding-group), read-only. Worktree .worktrees/nz-election-funding-group,
branch change/nz-election-funding-group, base origin/main. Product diff: git diff origin/main...HEAD -- product/
(funding_page.py, styles.css, test_funding_page.py, funding_browser.py). Judge against REVIEW.md; page plan
intent/nz-election/pages/funding.md; design product/nz_election/DESIGN.md.

Check: every one of the 146 returns stays reachable without JavaScript (fragment :target reveals a group; print shows all);
parties/ links to funding/#<party_id> land with that group open; keyboard and screen-reader access to hidden groups
(display:none until targeted) is acceptable per REVIEW.md accessibility; the 1280 grid change does not overlap modules;
tests check behaviour and data, not markup or class names. Supervisor host evidence: pytest -k "funding or design"
78 passed incl. Chromium; origin/data build PASS 82 routes; funding/ 390 full height 4,430 px (was about 21,000);
1280x800 pace heading y 641; #act click shows its returns; screenshots /tmp/fg/f-390-full.png, /tmp/fg/f-1280.png,
/tmp/fg/f-390-target.png (pass 4: look at them).

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
