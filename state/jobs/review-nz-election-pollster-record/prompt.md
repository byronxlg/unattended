Fresh-context review of nz-election-pollster-record, read-only. Worktree .worktrees/nz-election-pollster-record,
branch change/nz-election-pollster-record, head 49da422. PR body (`gh pr view` on the branch) is a claim to check.
Diff: git diff main...49da422. Judge against REVIEW.md and the brief state/jobs/nz-election-pollster-record/prompt.md
(main checkout).

Check: (1) every scored pollster-year traces to a pinned capture with its source URL and licence, values match the
captures (spot-check at least five rows against the capture bytes); (2) the error arithmetic is exact and matches the
stated method (which result it compares to, which fieldwork window, month-only dates handled as documented);
(3) exclusions are listed with reasons and none is biased toward one pollster or bloc; (4) the loader rejects
malformed records (tests exist that would fail without each check); (5) no existing test on main weakened; (6) no
invented numbers, no "not available" text.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
