Verdict: **accept**.

No Important or nit findings.

- `product/nz_election/pipeline/night_boundary.py:226`: creates the lock file and passes temporary state into the real `night_start.main`; lock and reservation functions remain unpatched.
- `:239`: checks the actual ledger against the expected reservation, then verifies it remains unchanged at cutoff. Resetting `clock.seconds` makes both scenarios test the exact cutoff.
- `:289`: each scenario runs inside a fresh temporary directory with isolation guards. History and dispatch subprocess calls are mocked.

The product diff changes only the boundary drill. Production watchdog and tests are unchanged. Review limited to `REVIEW.md` and the three-dot diff; no tests run.