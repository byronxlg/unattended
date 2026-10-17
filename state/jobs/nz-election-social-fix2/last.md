Committed `58cc131`; never pushed.

Changed `social.py` and branch-owned `test_social_exclusions.py`:
- Decode failures stay fatal with original codes.
- Successful batches clear active failure diagnostics.
- Daily classification stops after 49 failures among 480 candidates.

Verification:
- Classification eval: `PASS classify: 2 classified, 1 excluded, check named`
- Query eval: `PASS query length 495 of 512`
- `uv run --with pytest pytest -q product/nz_election`: `477 passed in 176.64s (0:02:56)`
- `bin/lint`: `lint ok (403 text files)`
- Requested fixture command: `PASS social`

Protected tests unchanged. [last.md](last.md) contains per-item details and verbatim outputs; uncommitted. No open questions.