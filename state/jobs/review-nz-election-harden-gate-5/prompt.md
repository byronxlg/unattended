Fifth fresh-context review of PR #83 (nz-election-harden-gate), read-only. Worktree .worktrees/nz-election-harden-gate,
branch change/nz-election-harden-gate, head dcf467d on main dc57e78. Fix round diff: git diff d406b7f..dcf467d; full
diff: git diff dc57e78...dcf467d. Judge against REVIEW.md.

The fourth review found that an array literal or an uncalled function containing night_live.py counted as the guard
(check_workflow_history.py:151). Fix-4 fails closed: only a top-level simple command that invokes the guard script is
guard evidence; any unsupported shell syntax in a run step voids that whole step's evidence. Known, accepted consequence:
night-live's real guard step is now unrecognised (false negative, strict). Invariant: the detector may under-recognise
a guard, never over-recognise one. Check it holds and that no test on main at dc57e78 was weakened. Do not ask for a
full shell parser, and do not report false negatives (a real guard not recognised) as defects; report only cases
where text that does not run the guard counts as the guard, or a cadence or SKIP defect.
Supervisor host run on dcf467d: test_harden*.py 203 passed; 39 fail with check_workflow_history.py at d406b7f; lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
