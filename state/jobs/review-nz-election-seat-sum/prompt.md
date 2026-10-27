Fresh-context review of PR #106 (nz-election-seat-sum), read-only. Worktree .worktrees/nz-election-seat-sum,
branch change/nz-election-seat-sum, head 2b861f6. Diff: git diff origin/main...HEAD. Judge against REVIEW.md.

Test-only change: product/nz_election/tests/test_seat_sum.py pins two published vote vectors (origin/data
922492d and 0ae9bb4) to their seat allocation, overhang, majority and bloc sums (133 seats = 120 + overhang).

Check: the expected numbers follow from the allocator (Sainte-Lague, 5 percent or electorate threshold, overhang
kept) and the recorded electorate-win assumptions, not copied from output without reason; the test would fail on a
real regression (dropped overhang, wrong majority, bloc missing a party); it checks data, not markup; nothing on main
is weakened. Host: the file's 2 tests pass.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
