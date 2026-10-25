Sixth fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head e04e72b on main dc57e78. Fix round diff: git diff dcf467d..e04e72b; full
diff: git diff dc57e78...e04e72b. Judge against REVIEW.md.

The fifth review found that a decoded carriage return (or other non-printable character) counted as guard evidence
(check_workflow_history.py:179). Fix-5 voids any run step containing a non-printable or non-ASCII character before
tokenization and sets shlex whitespace to space, tab and newline. Invariant, unchanged: the detector may
under-recognise a guard, never over-recognise one. Check it holds and that no test on main at dc57e78 was weakened.
Do not ask for a full shell parser, and do not report false negatives as defects; report only cases where text that
does not run the guard counts as the guard, or a cadence or SKIP defect.
Supervisor host run on e04e72b: test_harden*.py 257 passed; 51 fail with check_workflow_history.py at dcf467d; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
