Verdict: **request changes**.

Critical: None.

Important:
- [night_deployed.py:243](/Users/byron/repos/unattended/.worktrees/nz-election-night-deployed/product/nz_election/tests/night_deployed.py:243): `night-data-transport` passes with zero responses regardless of whether polls have closed. Page errors also do not fail probe mode. Broken live initialization can therefore leave the static fallback and produce PASS without exercising transport. Require a successful response after opening, reject pending/inconclusive transport, and fail unexpected page errors.

Nit: None.

The three original findings are closed, with regression tests that would fail on `88f9367`. No existing assertion was weakened. Read-only in-memory probes confirmed the CORS and manifest fixes; the saved live record supports its PASS. Pytest was not run.