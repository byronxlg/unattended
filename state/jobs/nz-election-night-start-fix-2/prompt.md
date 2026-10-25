# Follow-up 2 on PR #78 (fix-2): lock must outlive a killed wrapper

Second fresh review, one Important, confirmed by the supervisor reading bin/night-watchdog:

`bin/night-watchdog` takes `flock` on `state/night-start.lock`, then `subprocess.Popen(command, start_new_session=True)`.
Popen closes inherited fds by default, so only the wrapper holds the lock. If the wrapper is SIGKILLed
(bin/tick hard kill, launchd), `finally` never runs, the lock is released, and the detached worker keeps
running in its own session. The next tick takes the lock and can dispatch a second night-live run while
the orphan can still dispatch. Reviewer reproduced: "SIGKILL wrapper: lock reacquired / orphan reached dispatch".

Invariant: no second dispatch attempt may start while any process from an earlier attempt can still
dispatch. Where it is enforced is your choice (for example the worker keeps the lock's open file
description, via pass_fds, or the worker takes the lock itself, or the worker stays in the wrapper's
group); keep the existing timeout cleanup, marker and boundary behaviour.

Done when:
- a test kills the wrapper with SIGKILL while the worker is still running, and shows a second watchdog
  call does not dispatch until the worker has exited (the test fails on dcf30ad);
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py` passes;
- `bash -n bin/tick` exits 0; `bin/lint` prints ok.

Tests on main at the base sha are not edited; this branch's own tests may move with the change.
Commit in the worktree, do not push, do not commit last.md.
