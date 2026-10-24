Committed `3562819`: added `night_deployed.py`, `test_night_deployed.py`, and updated `runbook/night.md`.

Verification:

- Targeted pytest: `3 failed, 10 passed in 3.66s`
- Full pytest: `4 failed, 2118 passed, 2 errors in 610.48s`
- `bin/lint`: `lint ok (897 text files)`

All failures/errors stem from sandbox-denied Chromium launch. Live and local attempts each printed:

```text
FAIL deployed-probe: execution
FAIL deployed-rehearse: execution
FAIL deployed-faults: execution
```

Browser acceptance, screenshots, and replay timings require a host rerun. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-deployed/last.md). Records and report remain untracked; nothing pushed.