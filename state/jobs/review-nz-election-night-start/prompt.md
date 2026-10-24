Fresh-context review of PR #78 (nz-election-night-start), read-only. Worktree .worktrees/nz-election-night-start,
branch change/nz-election-night-start, head 5bc00f2. Diff: git diff e5812e3...5bc00f2. Judge against REVIEW.md.

The change starts election night without a human: two cron starts on 7 Nov in nz-election-night-live.yml, a fail-closed
decision script product/nz_election/pipeline/night_start.py reusing night_live.require_open, and a watchdog in bin/tick
(the live host loop, every 10 min) that dispatches night-live once if no run exists since opening.

Check in particular: the cron times against 19:00 NZDT poll close (06:00Z 7 Nov) and the s197 freeze; what END in
night_live.py means and whether "instant < END + 10 min" and the createdAt >= END comparison are the intended bounds;
that the watchdog cannot dispatch outside the window, cannot dispatch twice (in-progress or completed runs since opening),
and cannot break or delay bin/tick on any failure (gh missing, network down, uv slow; timeouts); the new 8 Nov 06:00Z
upper bound; that tests exercise the decision boundaries and nothing weakens an existing check (one trigger assertion moved).
Host: test_night_operation.py and test_workflows.py 51 passed, bash -n bin/tick ok, bin/lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
