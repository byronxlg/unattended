Fresh-context review of PR #80 (nz-election-night-stop), read-only. Worktree .worktrees/nz-election-night-stop,
branch change/nz-election-night-stop, head 95387fe on main bd53141. Whole change: git diff bd53141...95387fe.
Judge against REVIEW.md; read intent/nz-election/plan-week-after.md increment 1 (bounded stop) and the runbook
section the change adds (product/nz_election/runbook/night.md).

Goal of the change: the election night loop (night-live workflow, bin/night-watchdog path) and the browser polling in
web/night-live.mjs both stop at one shared cutoff constant, 8 Nov 06:00Z, and the published package says the loop
ended and when, so a reader is not left watching a page that polls nothing.

Check: one constant, not two copies that can drift; the cutoff holds in the workflow, the Python loop and the browser
(no poll after it, including on tab resume); the before-cutoff behaviour on election night is unchanged; the ended
state copy obeys the absent-text rule (no "not available"); nothing weakens an existing check. One assertion on main
moves: test_result_states.py live_package({}) now carries loop_ended and loop_ends_at; confirm that is the contract
moving, not a weaker check.
Host on 95387fe: test_result_states.py and test_night_operation.py 106 passed; full product suite on 0a45eab (pre-rebase)
2434 passed incl. browser. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
