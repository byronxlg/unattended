Fourth fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head d406b7f on main dc57e78. Fix round diff: git diff 191c461..d406b7f; full
diff: git diff dc57e78...d406b7f. Judge against REVIEW.md.

The third review found that Bash ANSI-C quoting ($'...') yielded a false night_live.py invocation
(check_workflow_history.py:126). Fix-3 ignores guard evidence from the first line containing $' onward (fails closed:
a workflow using $' before its guard reports the guard missing). Invariant: the guard is declared only by a `run:` step
whose shell commands actually invoke the guard script; quoted text, echo arguments and comments never count; anything
the detector cannot parse fails closed, never open. Check it holds and that no test on main at dc57e78 was weakened.
Do not ask for a full shell parser.
Supervisor host run on d406b7f: test_harden*.py 162 passed; 3 fail with check_workflow_history.py at 191c461; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
