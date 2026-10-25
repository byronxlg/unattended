Verdict: **accept**

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

`bin/night-watchdog:28`: `pass_fds` preserves the same locked open file description across fork/exec. Wrapper SIGKILL leaves the worker holding the lock; worker exit releases it. No persistent lock leak found.

`bin/night-watchdog:29` and `:39`: outer timeout and process-group cleanup remain intact. `product/nz_election/pipeline/night_start.py:38`: dispatch-time window recheck remains intact. No existing checks weakened.

Read-only probes against the actual wrapper:
```text
PASS: wrapper SIGKILL retains lock while worker lives
PASS: worker exit releases lock and permits next attempt
PASS: outer timeout kills worker and releases lock
```

Pytest not run. UV-path evidence comes from the supplied host regression results and test inspection. No files changed.