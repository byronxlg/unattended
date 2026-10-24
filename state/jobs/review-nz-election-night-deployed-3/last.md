Verdict: **request changes**

Critical: None.

Important:
- [night_deployed.py:225](/Users/byron/repos/unattended/.worktrees/nz-election-night-deployed/product/nz_election/tests/night_deployed.py:225): Phase uses `Date.now()` from the page’s mutable JavaScript context. A page override can report pre-close after actual close, allowing zero responses to pass. Executing the actual evaluator in Node with `Date.now = () => 0` returned `now_ms=0`; the Python probe then accepted zero responses. Use an independent host clock and add a regression where host time is post-close while page time is pre-close.

Nit: None.

Read-only probes confirmed:

- Post-close zero responses: `36659a4 PASS` → `2ff2d4f FAIL`.
- Pre-close page error: `36659a4 PASS` → `2ff2d4f FAIL`.
- Manifest fetch failure remains `FAIL`.
- CORS network failures remain `INCONCLUSIVE`, preventing acceptance.
- Fixture staging remains beneath the record directory.
- Unexpected page errors fail every mode through the final `page_errors` check.

No pytest or browsers run; no files changed.