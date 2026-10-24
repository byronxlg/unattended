Blocked by conflicting requirements. [test_increment_two_regressions.py:200](/Users/byron/repos/unattended/.worktrees/nz-election-polls-refine/product/nz_election/tests/test_increment_two_regressions.py:200) explicitly requires a separate overhang segment. Removing it violates a protected test; AGENTS.md instructs stopping when a test is wrong.

No code changed or committed. Findings recorded in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-polls-refine/last.md).

Verification:
- Strip probe: `FAIL (nat occurs twice)`
- `bin/lint`: `lint ok (858 text files)`
- Requested pytest run interrupted: `KeyboardInterrupt`, exit 130.
- Screenshots not run.

Supervisor needs to reconcile the overhang assertion with the single-segment requirement.