Fresh-context review of PR #73 (nz-election-polls-refine), read-only. Worktree .worktrees/nz-election-polls-refine,
branch change/nz-election-polls-refine, head ebce3c7. Diff: git diff 170bf94...ebce3c7 -- product. Judge against REVIEW.md.

Context: refinement round on the polls page (Page plan intent/nz-election/pages/polls.md). build.strip() printed
p.upper(), so The Opportunity Party read "OPP"; now abbreviation() gives TOP. polls.css makes the since-date in the
change summary inherit its sentence's size and face. Check: every other caller that prints a party abbreviation
from the id (grep p.upper and .upper() in pipeline/ and web/*.mjs) is consistent or named; the label is escaped;
aria-label still uses the full name; the new test fails on 170bf94; no pre-existing test edited.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.

## Second round
This is the second fresh review of PR #73. The first review found one Important: web/coalitions.mjs:119 rendered the client strip label as p.toUpperCase() (OPP), not TOP. Fix-1 is ebce3c7 (build.py emits data-abbreviation on each coalition row, coalitions.mjs reads it, seven-party markup parity tests in test_polls_refine.py). Judge that the finding is fixed and nothing regressed. Note: no route on the current build loads coalitions.mjs (PR #71 replaced the polls explorer with anchor spans), so product/nz_election/tests/coalitions_browser.py times out on main and on this branch alike; that is a pre-existing, separate defect, not a finding against this PR.
