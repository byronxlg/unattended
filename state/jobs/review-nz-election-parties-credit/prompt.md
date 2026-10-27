Fresh-context review of PR #107 (nz-election-parties-credit), read-only. Worktree .worktrees/nz-election-parties-credit,
branch change/nz-election-parties-credit, head fa33005, stacked on change/nz-election-funding-page (3dcc564).
Diff: git diff 3dcc564...HEAD. Judge against REVIEW.md. Brief: state/jobs/nz-election-parties-credit/prompt.md; page
plan intent/nz-election/pages/parties.md; design product/nz_election/DESIGN.md.

Check: portrait credit (author and licence, with link) still present for every portrait and now below the party's
answer; the licence obligations of each photo (CC BY-SA and others) are still met on the page or via a link (the
processing note left the page: is "changes were made" required by any licence in snapshots, and if so is it still
reachable?); home party cards keep share and change whole at 360 and 390; the two moved assertions in
test_parties_captions.py and test_parties_refine.py follow the removed copy and weaken nothing else; tests check data,
provenance and behaviour, not markup. Supervisor host evidence: pytest -k "parties or home or design" 230 passed incl.
Chromium; origin/data build PASS 82 routes; screenshots /tmp/pc-parties-390.png, /tmp/pc-parties-1280.png,
/tmp/pc-home-cards-390.png (read them if you can).

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line, and the three weakest
visual points. You cannot approve.
