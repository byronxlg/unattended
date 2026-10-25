Verdict: **request changes**

Critical: none.

Important:

- `bin/night-watchdog:26` and `:37`: **Killing the wrapper can break serialization.** SIGKILL releases its lock but bypasses `finally`, leaving the detached worker alive. Another tick can acquire the lock and dispatch while the original worker can still dispatch; neither has written the marker yet. A read-only subprocess probe reproduced:
  ```text
  SIGKILL wrapper: lock reacquired
  orphan reached dispatch
  ```
  Make worker lifetime and lock ownership remain coordinated when the wrapper dies. Add kill-path coverage; `test_night_operation.py:531` exercises timeout cleanup, but not wrapper termination.

Nit: none.

Other checks: timeout cleanup and subsequent lock acquisition passed isolated probes. Failed workers left no marker. The production command cannot create a rehearsal marker; failed Actions runs intentionally count as attempts under the documented policy. Dispatch-time rechecking uses the same guard and correctly rejected the closing boundary. No existing check was found weakened.

Verification: `python3 -B -c` isolated probes; `bash -n bin/tick` exited 0 with no output. No pytest, network calls, or file changes.