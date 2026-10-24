# Fix round 1 for PR #76 (night deployed probe)

The fresh review of PR #76 requested changes. Fix all three Important items on this branch
(change/nz-election-night-deployed, worktree .worktrees/nz-election-night-deployed). Fix job: tests on
main at the base sha f406321 do not change; this branch's own tests (test_night_deployed.py) move with
the fix. Nothing weakens an existing check.

1. `product/nz_election/tests/night_deployed.py:154` CORS check passes on any failure (DNS, TLS,
   timeout, HTTP error, empty response). Distinguish expected CORS blocking from an inconclusive
   network failure: for example confirm from the host side (a plain HTTP fetch outside the browser)
   that the upstream is reachable and returns a non-empty body, and only then count the browser's
   failed fetch as CORS evidence; an unreachable upstream is INCONCLUSIVE (not PASS) with its reason.
   If the browser fetch is readable, validate the response instead of passing.
2. `night_deployed.py:84` provenance: a failed manifest fetch leaves both SHAs null and records no
   failure. Require a successful manifest response with valid code and data SHAs (40 hex) before PASS.
3. `night_deployed.py:236` `TemporaryDirectory()` stages fixture data outside `artifacts/`. Stage it
   beneath the run's record directory.

Definition of done (paste output in last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py` passes, with new
  tests for items 1 and 2 that fail on 88f9367 (injected transport, no network).
- `bin/lint` prints ok.
- Chromium may not launch in the sandbox; the supervisor runs --probe on the host. Say what you could
  not run.
- Commit on the branch, do not push. Do not commit last.md.
