Fresh-context review of PR #105 (nz-election-funding-page), read-only. Worktree .worktrees/nz-election-funding-page,
branch change/nz-election-funding-page, head 3dcc564. Diff: git diff origin/main...HEAD. Judge against REVIEW.md.
Brief: state/jobs/nz-election-funding-page/prompt.md; page plan intent/nz-election/pages/funding.md; design
product/nz_election/DESIGN.md.

Check: the page answers the plan's questions in the plan's order; every figure traces to an EC return in
donations.json with its link and retrieved date; totals are declared returns over NZD 20,000, never called total
funding; all 146 returns reachable; absence handled without "not available" text; nav gains one link without breaking
the header at 360/390; route contracts move with the registered set and nothing is weakened; tests check data,
provenance and behaviour, not markup. Supervisor host evidence: origin/data build PASS 82 routes, funding/ at 390
and 1280 looked at, no sideways scroll; screenshots /tmp/funding-shot-390.png and /tmp/funding-shot-1280.png (read
them if you can); host Chromium run in progress.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line, and the three weakest
visual points. You cannot approve.

Second round: the branch head is now 3dcc564 (fix-1 for the first review's finding: home funding summary lacked a dated EC credit). Review the whole diff against origin/main again; confirm the earlier finding is resolved and nothing regressed.
