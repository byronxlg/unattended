Fresh-context review of nz-election-m3-live (PR #65), read-only. Worktree .worktrees/nz-election-m3-live,
branch change/nz-election-m3-live, head 727561e. The PR body (`gh pr view 65`) is a claim to check.
Diff: git diff main...727561e. Judge against REVIEW.md, intent/nz-election/plan-m3.md increment 5 (transport via
Actions, amended 22 Oct), intent/nz-election/pages/night.md, and the brief state/jobs/nz-election-m3-live/prompt.md.

Check: (1) the Actions night cycle fetches media.election.net.nz XML server-side and publishes only validated
results; failed or partial fetches keep the last good snapshot and say so with a time; (2) the publication freeze
(Electoral Act s197, 00:00 to 19:00 NZDT 7 November) is one shared rule enforced in every publishing path,
including pages.yml and the new cycle, with boundary tests at both instants; (3) replay or demo data can never be
labelled or served as live 2026 results; (4) the browser polling: no fetch while hidden, one on resume, backoff on
errors, and the fix-1 harness change (727561e) did not weaken any assertion; (5) tests on main at the merge base
are not weakened; (6) no secrets, no new paid service, workflow permissions minimal.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
