Fresh-context review of nz-election-snapshots, read-only. Worktree .worktrees/nz-election-snapshots,
branch change/nz-election-snapshots, head c737231 on main 05b311b. PR #42 (`gh pr view 42`).
Diff: git diff 05b311b..c737231. Judge against REVIEW.md, the brief state/jobs/nz-election-snapshots/prompt.md
(main checkout) and issue #40 (`gh issue view 40`). The engineer's account is in the PR body and is a claim to check.

Check: (1) spot-check at least five numeric records against their source URLs where reachable (history 2023
National 38.08 vs the EC figure, a Port Waikato 2023 count, two enrolment rows, one candidate list rank); report
any mismatch with the source's value; (2) every record carries source URL, retrieval time and licence, and photo
licences match their Commons file pages (author, licence, derivative note); (3) no raw social posts, handles,
keys or personal data beyond public candidacy facts; (4) the loader and tests fail on a malformed snapshot (missing
source, bad licence, unknown party id) and are offline; (5) no test on main weakened; (6) nothing invented to fill a
gap (fuzzy joins, inferred ranks, secondary-source substitution).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
