Fourth fresh-context review of PR #94 (nz-election-night-design), read-only. Worktree .worktrees/nz-election-night-design,
branch change/nz-election-night-design, head 16f24ee. Diff since the accepted third review: git diff 51a52c9..16f24ee
(c840c83 merges main incl. #97 hex-native map; 8244ce1 replaces the night "All N majority combinations" <details> with an
open section and list, to satisfy main's test_disclosures PROSE_DISCLOSURE rule; 16f24ee matches that list in the branch's
own browser test by its rendered accessible name, which the build prefixes with "Static "). Judge against REVIEW.md.
Brief: state/jobs/nz-election-night-design/prompt.md; page plan intent/nz-election/pages/night.md; design
product/nz_election/DESIGN.md.

CI was red on main's test_disclosures (night/index.html details without a table) and test_verify_required x2
(CAMPAIGN_DATA from that disclosure). Check those are resolved without weakening any check on data, provenance, absence or
accessibility, that the merge of main kept #97's map intact, and that no new test pins markup, class names or bytes.
Supervisor host run with Chromium: test_disclosures, test_verify_required, test_design, test_home*, test_night*,
test_waterfall 450 passed, 1 failed (the branch's list locator, fixed in 16f24ee; test_night_design_followup 5 passed after).
Combinations list looked at at 1280, night/ 390 top looked at on a replay build.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
