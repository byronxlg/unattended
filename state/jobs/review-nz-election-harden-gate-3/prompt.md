Third fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head 191c461 on main dc57e78. Fix round diff: git diff 9c5c5fc..191c461; full
diff: git diff dc57e78...191c461. Judge against REVIEW.md.

The second review asked for: guard detection that keeps shell quote state across lines, so (1) a newline inside a quoted
string never acts as a command separator (no false pass for `echo '<newline> python3 .../night_live.py'`), (2) a comment
does not consume the command-separating newline (`set -e # setup` then a real invocation counts), (3) a backslash-continued
invocation counts. Invariant: the guard is declared only by a `run:` step whose shell commands actually invoke the guard
script; quoted text, echo arguments and comments never count. Check it holds, including `#` inside quotes or words
(`a#b`), escaped quotes, heredocs if relevant, and that no test on main at dc57e78 was weakened. Do not ask for a full
shell parser.
Supervisor host run on 191c461: test_harden.py 158 passed; 9 fail with check_workflow_history.py at 9c5c5fc; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
