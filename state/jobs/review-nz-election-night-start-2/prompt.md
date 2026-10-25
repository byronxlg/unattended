Second fresh-context review of PR #78 (nz-election-night-start), read-only. Worktree .worktrees/nz-election-night-start,
branch change/nz-election-night-start, head dcf30ad. Diff: git diff e5812e3...dcf30ad. Judge against REVIEW.md.

The change starts election night without a human: cron starts on 7 Nov in nz-election-night-live.yml, a fail-closed
decision script product/nz_election/pipeline/night_start.py reusing night_live.require_open, and bin/night-watchdog
called from bin/tick (the live host loop, every 10 min) that dispatches night-live once if no run exists since opening.
The first review asked for: an outer timeout so the watchdog cannot hang bin/tick, serialized check-and-dispatch so two
ticks cannot both dispatch, and a window check at dispatch time, not only at decision time. fix-1 (dcf30ad) claims a
60 s timeout, a lock, a persistent success marker and a clock recheck before dispatch.

Check that those three items are actually closed (lock is released on every exit path including timeout and kill; a stale
lock cannot block the night forever; the success marker cannot suppress a needed dispatch, for example a marker left by a
rehearsal or a failed run; the recheck uses the same bounds as night_start.py); that nothing weakens an existing check;
that tests exercise the new paths. Host: test_night_operation.py and test_workflows.py 54 passed, bash -n bin/tick ok,
bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
