Fresh-context review of PR #109 (nz-election-funding-nits), read-only. Worktree .worktrees/nz-election-funding-nits,
branch change/nz-election-funding-nits, head bf2d78d, stacked on change/nz-election-parties-credit (fa33005).
Diff: git diff fa33005...HEAD. Judge against REVIEW.md. Brief: state/jobs/nz-election-funding-nits/prompt.md; page
plan intent/nz-election/pages/funding.md; design product/nz_election/DESIGN.md.

Check: every one of the 146 returns and its provenance (EC source, retrieved date) still reachable; whole-dollar
summaries are rounding of the exact figures and the exact amounts remain on each row; full party names match the EC
register (Te Tai Tokerau Party is a registered party); stacked donor rows at 390 keep name, amount and date together and
readable; tests check data, provenance and behaviour, not markup. Supervisor host evidence: pytest -k "funding or
design" 75 passed incl. Chromium; origin/data build PASS 82 routes; screenshots /tmp/sh-fn/funding-390.png (21,000 px
full page), /tmp/sh-fn/top.png, /tmp/sh-fn/mid.png, /tmp/sh-fn/funding-1280.png.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line, and the three weakest
visual points. You cannot approve.
