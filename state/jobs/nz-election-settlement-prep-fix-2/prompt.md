# Fix 2 for PR #117 (settlement capture prep)

Second fresh review (request changes), confirmed by the supervisor from its probes:

1. Important: `product/nz_election/pipeline/settlement_capture.py:84` (the bundle validation boundary)
   does not give named, sanitized errors for malformed bundles. Null or numeric JSON raises an uncaught
   `TypeError`; empty input raises an unnamed `JSONDecodeError`; an input-controlled key is echoed in a
   message (`ValueError INVALID_TIMESTAMP: envelope.data.<attacker key>.generated_at`).
   Invariant: every failure at this boundary exits nonzero with one stable named code and no text taken
   from the input (no keys, values or exception strings from upstream). Catch at the CLI boundary, as
   `advance_preflight.py` does after its fix-3. Add tests asserting the exact code and the absence of a
   sentinel string for: empty file, `null`, a number, a list, a dict with a sentinel key carrying a bad
   timestamp.
2. Nit: `product/nz_election/runbook/night.md:524` passes the literal `PRE_IMPORT_DATA_SHA` although a
   shell variable is defined above; use `data_sha="$PRE_IMPORT_DATA_SHA"` and make the
   `SETTLED_DATA_SHA` assignment and substitution equally explicit, so copied commands do not fail
   `NIGHT_DATA_SHA`.

Constraints: fix job; tests on main at the PR's base sha are untouched; this branch's own tests may move
with the fix. Commit in the worktree, do not push.

Done when:
`uv run --with pytest pytest -q product/nz_election/tests/test_result_import*.py product/nz_election/tests/test_settlement*.py`
passes, the new cases fail with settlement_capture.py at a971810, and `bin/lint` prints `lint ok`.
Write commands and output in last.md.
