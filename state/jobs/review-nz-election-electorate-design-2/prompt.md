Second fresh-context review of PR #98 (nz-election-electorate-design), read-only. Worktree .worktrees/nz-election-electorate-design,
branch change/nz-election-electorate-design, head 9488223. Diff: git diff origin/main...9488223. Judge against REVIEW.md. Brief:
state/jobs/nz-election-electorate-design/prompt.md; page plan intent/nz-election/pages/electorate.md; design product/nz_election/DESIGN.md.
First review (state/jobs/review-nz-election-electorate-design/last.md) asked that branch tests stop pinning markup.

Since then: ec403fc rewrote test_electorate_page_plan.py with semantic checks (headings, links, names, route resolution);
9488223 (supervisor) moved the enrolment and Policy.nz actions after the candidate cards in electorate_pages.py detail() to match
the plan's order, and restored main's direction in test_electorate_policy_links.py and route_checks.py 'candidate-first order',
which 1a23dc1 had inverted. Check: no branch test pins markup, class names or bytes; every edit to a test or check on main is
justified by a registered contract moving or restores main; plan order holds (candidates, is-this-mine, policy, previous result);
absent data is absent. Supervisor host: 36 targeted plus 44 design (Chromium) passed, lint ok, origin/data build PASS 81 routes,
Nelson 1280 and Waiariki 390 looked at. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
