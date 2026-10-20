Second fresh-context review of M3 increment 1 (advance voting), read-only. Worktree
.worktrees/nz-election-m3-advance, branch change/nz-election-m3-advance, head 2f6c050 on 6bbc873
(base 0f21ab5). PR #48 (`gh pr view 48 --comments`) holds the first fresh review (request changes:
descriptor failures, structural absence checks, per-row voting-window filtering) and the supervisor
reviews. Fix commit: git show 2f6c050. Judge against REVIEW.md. The engineer's account
(state/jobs/nz-election-m3-advance-fix-1/last.md) is claims to check.

Host evidence: 922 passed, lint ok on 2f6c050; host screenshot harness PASS 79 routes 308 images on
6bbc873 (populated and production builds).

Check: (1) each first-review item is fixed at every place it applies, with a test that would fail
on 6bbc873; (2) the fix weakened no test on main at 0f21ab5 and moved no check; (3) the disclosure of
filtered rows is visible to readers; (4) nothing new regressed.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
