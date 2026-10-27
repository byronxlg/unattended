Fresh-context review of PR #104 (nz-election-night-labels), read-only. Worktree .worktrees/nz-election-night-labels,
branch change/nz-election-night-labels, head 7933c98. Diff: git diff origin/main...HEAD. Judge against REVIEW.md.
Brief: state/jobs/nz-election-night-labels/prompt.md; page plan intent/nz-election/pages/night.md; design
product/nz_election/DESIGN.md.

Check: replay and final-archive reporting lines no longer present a bare clock as an update time and say what the
count is; the live feed keeps its update time; bloc labels come from one shared source and the parties remain named
on the module; tests check behaviour, not markup. Supervisor host evidence: pytest -k night 364 passed (incl.
Chromium), lint ok, origin/data build PASS 81 routes, night/ at 390 and 1280 looked at, no sideways scroll;
screenshots /tmp/nl-night-390.png and /tmp/nl-night-1280.png (read them if you can).

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
