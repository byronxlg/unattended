Committed `2a2c506`; not pushed.

- Restored freeze notice and both links in every night phase and replay frame.
- Added independent route gate and active-build regression tests.
- Protected tests unchanged.

Verification:
- Baseline `eb4a0d0`: 4 regression failures; fixed: 6 passed.
- Product tests: **1833 passed, 2 errors**, both Chromium sandbox launch failures.
- Populated verification: `PASS night`, `PASS all`.
- Lint: `lint ok (604 text files)`.

Evidence in uncommitted `last.md`. Browser verification remains for the host.