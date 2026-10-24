Committed `1ff85f3`. Added Harden CLI, workflow-history checker, injected-runner tests and runbook instructions.

Verification:

- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py`: `53 passed in 4.67s`
- `bin/lint`: `lint ok (879 text files)`
- `uv run --with pytest pytest -q`: `1 failed, 2333 passed, 2 errors in 631.92s`

All three full-suite issues were Chromium launch failures: macOS `Permission denied (1100)`.

Offline command:
```sh
bin/nz-election-harden --offline --data /tmp/nz-harden-fixture/data --site /tmp/nz-harden-fixture/site
```
Last line:
```text
FAIL harden: eval pages-home-bytes-live (SKIP)
```

Seven offline evals and 71 freeze tests passed. The gate also correctly rejected missing night/waterfall verification lines.

[Report]( /Users/byron/repos/unattended/.worktrees/nz-election-harden/last.md) remains uncommitted. Outstanding: browser-capable full-suite rerun and live milestone evidence.