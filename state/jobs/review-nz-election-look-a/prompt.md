Fresh-context review of L-a (538 look), read-only. Worktree .worktrees/nz-election-look, branch
change/nz-election-look, commits 28c8771 and 390ac75 on main 091c449 (git diff 091c449...HEAD).
PR #33 (`gh pr view 33 --comments`) carries the supervisor's review; do not repeat it, look for
what it misses. Intent: intent/nz-election/look-538.md. Briefs: state/jobs/nz-election-look-a/
prompt.md and followup-1.md on main. The engineer's account (state/jobs/nz-election-look-a*/last.md)
is claims to check, not evidence. Judge against REVIEW.md.

Screenshots from the host harness are in .worktrees/nz-election-look/artifacts/la-screenshots/fix1/
(home, polls, an electorate, night at 360, 390 and 1280): judge them against the look-538.md
targets (type, colour, hierarchy, contrast, tap targets).

Check, in this order:
(1) Every number in the hero has its source line; group totals are computed from the same
allocation as the party seats, never hardcoded; config/seat-groups.json membership is sourced.
(2) Fonts: self-hosted, OFL texts present, first-view byte budgets and the CSS budget enforced by
tests, not just met today.
(3) No fragment id or route main published is lost; no test pin moved weaker than main.
(4) Contrast of the new ink, bloc colours and notice band against WCAG AA; dark mode still works.
(5) Withheld-data and empty states read as reader copy, not internal messages.

Output: verdict (accept or request changes), then findings as Critical / Important / Nit with
file:line and a one-line fix each. No edits.
