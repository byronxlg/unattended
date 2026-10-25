Seventh fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head 2c5342f on main dc57e78. Fix round diff: git diff e04e72b..2c5342f; full
diff: git diff dc57e78...2c5342f. Judge against REVIEW.md.

The sixth review found that a folded YAML block scalar (joined with spaces) counted as guard evidence
(check_workflow_history.py:233). Fix-6 makes folded scalars provide no guard evidence. Invariant, unchanged: the
detector may under-recognise a guard, never over-recognise one. Check it holds and that no test on main at dc57e78 was
weakened. Do not ask for a full shell parser, and do not report false negatives as defects; report only cases where
text that does not run the guard counts as the guard, or a cadence or SKIP defect.
Supervisor host run on 2c5342f: test_harden*.py 262 passed; 6 fail with check_workflow_history.py at e04e72b; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
