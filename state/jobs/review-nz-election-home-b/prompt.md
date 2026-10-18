Fresh-context review of home increment H-b, read-only. Worktree .worktrees/nz-election-home-b,
branch change/nz-election-home-b, one commit 748fc5f on main 7065377 (git diff main...HEAD).
PR #31 (`gh pr view 31 --comments`) carries the supervisor's review; do not repeat it, look for
what it misses. Intent and plan: intent/nz-election/home.md, intent/nz-election/plan-home.md
(H-b and the supervisor decisions, including the authorized pages.yml OG step). The engineer's
account is state/jobs/nz-election-home-b/last.md on main: claims to check, not evidence. Judge
against REVIEW.md.

Check, in this order:
(1) pages.yml: the OG step runs after verification and before upload, cannot publish during the
s197 freeze, fails the deploy on a missing or wrong-size PNG, and adds no secrets or permissions.
(2) Every one of the 79 routes has og:image, og:title, og:description and canonical URLs that
resolve under /unattended/nz-election/; no image references a file the build does not produce.
(3) /night/ makes no claim about results before 19:00 NZDT 7 November; the countdown is computed
at build time against NZDT and is right on either side of the daylight boundary and on the day.
(4) Electorate pages: candidates first, every fragment and id main published still present.
(5) Moved pins (screenshots.py, test_home.py, runbook counts): each moved because the route or
image set moved, nothing weaker than main.
(6) The OG templates and cards: no raw upstream text without escaping, no number without its
source line.

Output: verdict (accept or request changes), then findings as Critical / Important / Nit with
file:line and a one-line fix each. No edits.
