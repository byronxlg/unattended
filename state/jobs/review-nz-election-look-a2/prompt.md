Fresh-context review of L-a2, read-only. Worktree .worktrees/nz-election-look-a2, branch
change/nz-election-look-a2, commit 972ed1a on main a39c2ec (git diff a39c2ec...HEAD). PR #35
(`gh pr view 35 --comments`) carries the supervisor's review; do not repeat it, look for what it
misses. Intent: intent/nz-election/look-538.md; spec intent/nz-election/spec.md (Others-as-remainder
exception). Brief: state/jobs/nz-election-look-a2/prompt.md. The engineer's account
(state/jobs/nz-election-look-a2/last.md) is claims to check, not evidence. Judge against REVIEW.md.

Screenshots from the host harness on live data refreshed with this code are in
.worktrees/nz-election-look-a2/artifacts/a2-screenshots/ (home and polls at 360, 390, 1280, dark):
judge them against look-538.md (colour, hierarchy, contrast).

Check, in this order:
(1) Derived Others: bounded as the spec says, labelled and disclosed wherever it feeds a number;
a row it cannot derive stays withheld; nothing silently changes a published poll value.
(2) Bloc colours and bar order: computed from the same allocation as the party seats; overhang
handled; the 67 line correct.
(3) Social proof-of-concept band persists with sample size and dates in populated and stale states.
(4) No fragment id or route main published is lost; no test pin moved weaker than main.
(5) Contrast of the bloc colours against WCAG AA in light and dark.

Output: verdict (accept or request changes), then findings as Critical / Important / Nit with
file:line and a one-line fix each.
