Third fresh-context review of PR #78 (nz-election-night-start), read-only. Worktree .worktrees/nz-election-night-start,
branch change/nz-election-night-start, head ed64b0d. Diff: git diff e5812e3...ed64b0d. Judge against REVIEW.md.

The change starts election night without a human: cron starts on 7 Nov in nz-election-night-live.yml, a fail-closed
decision script product/nz_election/pipeline/night_start.py reusing night_live.require_open, and bin/night-watchdog
called from bin/tick (every 10 min) that dispatches night-live once if no run exists since opening.
Earlier reviews: (1) outer timeout, serialized check-and-dispatch, window check at dispatch time, closed by fix-1 dcf30ad;
(2) the lock was released when the wrapper was SIGKILLed while the detached worker (start_new_session) could still
dispatch. fix-2 ed64b0d passes the locked fd to the worker (pass_fds) and adds test_watchdog_lock_survives_wrapper_sigkill.

Check that item 2 is closed (the worker really holds the same open file description; no path where the worker exits and
the lock is held forever, or where a second tick dispatches while the first worker lives); that fix-2 did not reopen any
fix-1 item; that nothing weakens an existing check. Host: test_night_operation.py and test_workflows.py 56 passed, the
SIGKILL test fails with bin/ at dcf30ad, bash -n bin/tick ok, bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
