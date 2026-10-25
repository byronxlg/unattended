Fix round 1 for PR #85 (result import). Fresh review, Important, confirmed by the supervisor's reading:

result_import.py:104-114 reports PASS and dispatches Pages without confirming the publisher applied the transition.
A reachable pinned SHA can hold an older live capture than the current data head; publish.py:160-174 then keeps the
newer live data (keep_data=True) despite the requested settled or official state, so the published night family does
not match the verified transition. Reviewer probe: pinned 10:35, current 10:36, requested settled -> keep_data=True,
live retained.

Invariant: the import reports PASS and dispatches Pages only when the night family that will be published is the one it
verified for the requested state. Where that is enforced is yours to choose (reject the conflict before publication
with a named code, or verify the published family after the publisher runs); read publish.py and its tests first.

Constraints: tests on main at the PR base are protected (do not edit them); this branch's own tests move with it.
Add a regression for the probe above that fails on 3309ff2. Commit in the worktree, do not push.
Done: uv run --with pytest pytest -q on the tests your brief listed for result import plus test_publish*.py, all pass;
bin/lint prints lint ok; last.md names the regression and the command output.
