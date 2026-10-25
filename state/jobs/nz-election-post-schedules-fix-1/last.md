Committed `a8b74ff`, not pushed. Fixed live paid-call guards, clean cutoff handling/accounting, the shared night deadline, and official-results copy transitions.

Verification:

- Five regressions fail on `ca7bec1` and pass after the fix.
- Combined coverage: **215 passed, 1 failed**. Only failure: Chromium sandbox launch in `test_result_states_browser`.
- Broader social/pipeline checks: **256 passed**.
- 28 November home/vote/share copy checks passed.
- `bin/lint`: `lint ok (990 text files)`.

The exact requested command cannot run because `test_daily.py` is absent; both existing daily test files were used instead. Main’s tests remain unchanged.

Commands, outputs, and blockers are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-post-schedules/last.md), left uncommitted.