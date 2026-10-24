Fresh-context review of PR #73 (nz-election-polls-refine), read-only. Worktree .worktrees/nz-election-polls-refine,
branch change/nz-election-polls-refine, head e9ca98d. Diff: git diff 170bf94...e9ca98d -- product. Judge against REVIEW.md.

Context: refinement round on the polls page (Page plan intent/nz-election/pages/polls.md). build.strip() printed
p.upper(), so The Opportunity Party read "OPP"; now abbreviation() gives TOP. polls.css makes the since-date in the
change summary inherit its sentence's size and face. Check: every other caller that prints a party abbreviation
from the id (grep p.upper and .upper() in pipeline/ and web/*.mjs) is consistent or named; the label is escaped;
aria-label still uses the full name; the new test fails on 170bf94; no pre-existing test edited.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
