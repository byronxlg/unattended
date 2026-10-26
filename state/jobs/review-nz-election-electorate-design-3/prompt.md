Third fresh-context review of PR #98 (nz-election-electorate-design), read-only. Worktree .worktrees/nz-election-electorate-design,
branch change/nz-election-electorate-design, head 74c8fa5. Diff: git diff origin/main...74c8fa5. Judge against REVIEW.md. Brief:
state/jobs/nz-election-electorate-design/prompt.md; page plan intent/nz-election/pages/electorate.md; design product/nz_election/DESIGN.md.
Second review (state/jobs/review-nz-election-electorate-design-2/last.md) found the enrolment line below the 390 fold after 7-8
candidate cards and empty-candidate map link targets.

Since then: d6d8c0f compact phone candidate rows, repaired empty-list map destinations, added tests/electorate_phone_browser.py
(fold and empty cases) and a route test; 74c8fa5 (supervisor) writes the Boundary map in-page anchor directly because
build.link/safe_url drops fragment-only hrefs. Check: the second review's two findings are fixed; no branch test pins markup,
class names or bytes; plan order holds; absent data is absent; text stays at or above the 16 px reading floor.
Supervisor host: 140 passed incl. Chromium (fold and empty PASS on 5 electorates, largest list 11), lint ok, Nelson and
Christchurch East 390 looked at (screenshots in /tmp/e98/shots if readable). Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
