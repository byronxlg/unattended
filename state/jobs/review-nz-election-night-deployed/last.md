Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/tests/night_deployed.py:154`: CORS checks pass unconditionally. DNS/TLS failures, timeouts, HTTP errors and empty responses all produce PASS. Require evidence distinguishing expected CORS blocking from an inconclusive network failure; validate readable responses.
- `product/nz_election/tests/night_deployed.py:84`: Provenance never adds a failing check. A read-only function probe confirmed that fetch failure leaves both SHAs null and no failure recorded. Require a successful manifest response and valid code/data SHAs before PASS.
- `product/nz_election/tests/night_deployed.py:236`: `TemporaryDirectory()` writes fixture data under the system temporary directory, outside `artifacts/`. Place fixture staging beneath the record directory to meet the write restriction.

Nit: None.

The fault mode exercises the deployed client’s actual fetch/failure path through intercepted HTTP responses. Runbook commands match the CLI. Existing records contain both SHAs, but do not cover the failure cases above.

Verification: source review and read-only Python probes. No pytest or browser run; no files changed.