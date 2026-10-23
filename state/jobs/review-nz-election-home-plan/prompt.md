Fresh-context review of nz-election-home-plan (PR #64), read-only. Worktree .worktrees/nz-election-home-plan,
branch change/nz-election-home-plan, head cf770ea. The PR body (`gh pr view 64`) is a claim to check.
Diff: git diff main...cf770ea. Judge against REVIEW.md (question test in pass 4 first), the accepted page plan
intent/nz-election/pages/home.md, and the brief state/jobs/nz-election-home-plan/prompt.md.
Screenshots taken on the host: /tmp/home-plan/{before,night}-{390,1280}-{fold,full}.png (open them if you can read them).

Check: (1) the page answers the plan's questions in rank order, with dates, how to vote and the seat answer above
the fold at 390x844; (2) the date line's clock flips at the EC deadlines exactly (enrolment closes midnight
25 October NZDT, 2026-10-25T11:00Z), and the night handover at 2026-11-07T06:00Z uses only validated 2026 night data,
never replay or historical; (3) seat graphic totals are computed, not hardcoded (majority, overhang); the
"change since" delta compares like with like; range shading is labelled descriptive, not uncertainty; (4) every
figure has provenance; no "not available" text (ABSENT_TEXT gate); absent modules leave no empty anchors;
(5) every edited pre-existing test and check (test_home*, test_markets, test_absent_presentation,
test_design_review, home_checks.py, screenshots.py) moved with the module set without weakening a check on main;
(6) markets moved to methods/#home-markets with provenance and terms intact, and no inbound link to a removed home
fragment breaks; (7) accessibility: headings, landmarks, target size, map and picker keyboard use, chart text.
The supervisor already raised: hex markers beside the closest-margins list sit in a loose column away from their
rows; two near-duplicate all-electorates links. Confirm or refute.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
