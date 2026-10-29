# Follow-up 1: probe-states (PR #136), fresh review findings

The fresh review requested changes; both confirmed in `product/nz_election/tests/night_deployed.py`. Both files this branch touched (`night_deployed.py`, `test_night_deployed.py`) are this branch's own and move freely, including the new before-cutoff test. Tests on main at the base sha stay unchanged. Touch nothing else.

Invariant: the probe accepts a quiet page (zero night-data requests, retained or empty) only where the deployed client is meant to be quiet. Anywhere else, zero requests is the failure the probe exists to catch.

1. `stopped = phase['stopped'] or terminal is not None` (about line 334) lets a page labelled settled or official with zero requests pass before the shared `NIGHT_CLOSE` cutoff; base rejects it as `night-data-transport`. Read the client (`night-live.mjs` and `result_states.py`) to see whether a terminal state stops polling before the cutoff. If it does not, gate the quiet-page exception on `phase['stopped']` only. If it does, keep the terminal exception only for the states the client actually stops on, and name in last.md the client line that shows it.
2. `record.check('dated-fallback', dated or empty, ...)` (about line 298) accepts an undated empty shell at every time, including the live window. Bound the `empty` exception to post-stop (the same condition as item 1).

Add cases that fail on this branch's HEAD a32f35f: premature settled and official at 7 Nov 08:00Z with zero requests fail (unless item 1 finds the client stops there); an undated empty shell during the live window fails `dated-fallback`; post-stop retained, post-stop final and post-stop empty still pass; post-stop polling still fails.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py product/nz_election/tests/test_night_operation.py` passes (the sandbox cannot launch Chromium; say which cases it skipped), the new cases fail against night_deployed.py at a32f35f, one commit, no push.
