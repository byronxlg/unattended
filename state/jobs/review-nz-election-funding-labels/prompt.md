Fresh-context review of PR #110 (nz-election-funding-labels), read-only. Worktree .worktrees/nz-election-funding-labels,
branch change/nz-election-funding-labels, base origin/main. Diff: git diff origin/main...HEAD (one line in
product/nz_election/pipeline/home_graphics.py). Judge against REVIEW.md; page plan intent/nz-election/pages/funding.md;
design product/nz_election/DESIGN.md.

Check: the funding/ pace chart end labels round the exact cumulative cents to whole dollars half up, consistent with
funding_page.whole_money and the headline; exact amounts stay reachable (table equivalents, per-return rows); no other
caller of funding_steps changes. Supervisor host evidence: pytest -k "funding or home_graphics" 11 passed, bin/lint ok,
rendered labels $2,394,410 $2,291,751 $912,301 $833,000 $496,695 $491,660 $144,000.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
