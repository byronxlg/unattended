Fresh-context review of nz-election-vote-page, read-only. Worktree .worktrees/nz-election-vote-page,
branch change/nz-election-vote-page, head 3228381. PR #57 body (`gh pr view 57`) is a claim to check.
Diff: git diff main...3228381. Judge against REVIEW.md (question test in pass 4 first), the accepted page plan
intent/nz-election/pages/vote.md, and the brief state/jobs/nz-election-vote-page/prompt.md (main checkout).

Check: (1) the page answers the plan's questions in rank order, above-the-fold content matches the plan before and
from 26 October NZ time; (2) the NZ-midnight transition is correct (Pacific/Auckland, DST in effect, boundary
inclusive/exclusive as the plan says) and tested at both sides; (3) every date, link and fact comes from
snapshots/voting.json with provenance, nothing invented, no "not available" text (ABSENT_TEXT gate); (4) official
links point to EC domains; (5) contracts moved with the registered set (80 routes) without weakening any check on
main at its base; (6) the screenshot harness assertions for vote/ (answer 3 above 844 px, first-screen hrefs are EC
actions) actually test what they claim; (7) accessibility: landmarks, headings, target size, countdown not
announced every tick.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
