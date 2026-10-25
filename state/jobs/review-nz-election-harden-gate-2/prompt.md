Second fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head 9c5c5fc on main dc57e78. Fix round diff: git diff d891756..9c5c5fc; full
diff: git diff dc57e78...9c5c5fc. Judge against REVIEW.md.

The first review asked for: (1) per-date cadence: for each evaluated date the expected runs and allowed gap come only
from crons whose fields match that date, gap measured inside the active interval; (2) guard detection counts only a
`run:` step that invokes the guard, never comments or incidental text. Check both invariants hold, including cron
edge cases (ranges, lists, steps, day-of-month with day-of-week OR semantics, UTC day boundaries), multi-line `run: |`
blocks, a guard mentioned inside an echo string, and that no test on main at dc57e78 was weakened.
Supervisor host run on 9c5c5fc: test_harden.py 144 passed; 16 fail with check_workflow_history.py at d891756; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
