Fresh-context review of nz-election-parties-page, read-only. Worktree .worktrees/nz-election-parties-page,
branch change/nz-election-parties-page, head b389f5e. The PR body (`gh pr view change/nz-election-parties-page`) is a
claim to check. Diff: git diff main...b389f5e. Judge against REVIEW.md (question test in pass 4 first), the accepted
page plan intent/nz-election/pages/parties.md, and the brief state/jobs/nz-election-parties-page/prompt.md.

Check: (1) the page answers the plan's questions in rank order, picker and first party's polling number above the
fold at 390x844; (2) every fact has provenance: party-list-tops.json ranks traceable to the EC party-list PDF,
policy-links.json links only (no copied policy text), donation sums and top donors computed exactly from
donations.json including document_checked false rows, disclosed as such; (3) no "not available" text (ABSENT_TEXT
gate), absent lines omitted; (4) contracts moved with the registered set (81 routes) without weakening any check on
main at its base (look at every edited pre-existing test and check); (5) the new snapshot validators in
snapshots.py reject malformed input; (6) accessibility: landmarks, headings, target size, picker keyboard use,
portrait alt text and licence credits; (7) changes to home.py, home_charts.py, coalitions.mjs do not alter home or
polls output beyond the party links.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
