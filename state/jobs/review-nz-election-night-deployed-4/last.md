Verdict: **accept**.

- Critical: none.
- Important: none.
- Nit: none.

Fix confirmed at `product/nz_election/tests/night_deployed.py:236`. Read-only, in-memory probes with page time pre-close, host time post-close, and zero responses produced:
```text
2ff2d4f: before-close PASS
3d63029: after-close FAIL
```
The regression at `product/nz_election/tests/test_night_deployed.py:306` exercises this behavior without relying on the new argument.

Earlier safeguards remain intact: phase-aware transport, errors failing every mode, inconclusive CORS network failures, recorded manifest failures, and fixture staging beneath the record directory. No checks weakened.

Additional probes passed all 24 host-boundary/page-clock combinations. No pytest or browsers run; no files changed.