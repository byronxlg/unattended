# nz-election-boundary-watchdog: main is red on the boundary drill

Goal: make main's boundary drill pass again. PR #124 (boundary drill, product/nz_election/pipeline/night_boundary.py)
was built before PR #122 (product/nz_election/pipeline/night_start.py) merged. #122 made
`night_start.main(..., dispatch=True)` require shared state and the watchdog lock (`dispatch_lock`,
night_start.py:74-98: `state` argument or NIGHT_WATCHDOG_STATE, an existing `night-start.lock`, flock,
plus the recovery budget `reserve`, night_start.py:54). The drill's `watchdog()` (night_boundary.py:224-240)
still calls `night_start.main(clock.now, dispatch=True)` with no state, so on main:

- `uv run --with pytest pytest -q product/nz_election/tests/test_night_boundary.py` gives 2 failed 44 passed:
  watchdog-cutoff (WATCHDOG_CUTOFF) and watchdog-queued-cutoff (WATCHDOG_CALLS).
- Actions run 40736058756 (nz-election-night-rehearsal.yml, boundary_only=true, on b8d5b82) fails the same two.

Read first: night_start.py whole, night_boundary.py, test_night_boundary.py, test_night_operation.py's
watchdog/lock cases (how #122's own tests give state and lock).

Constraints: fix the drill harness (night_boundary.py) so it exercises the real watchdog path as
#122 shipped it: an isolated temp state dir with the lock file, the real dispatch_lock and reserve, the
same invariants (one dispatch before the cutoff, none when the history request crosses it, no work
after). Do not weaken night_start.py and do not edit tests on main (test_night_boundary.py,
test_night_operation.py). If an invariant cannot hold with #122's semantics, stop and say which.

Done:
`uv run --with pytest pytest -q product/nz_election/tests/test_night_boundary.py product/nz_election/tests/test_night_operation.py`
all pass; the drill entry point used by the rehearsal workflow prints PASS for watchdog-cutoff and
watchdog-queued-cutoff (state the command and its PASS lines); bin/lint ok; commit, do not push.
