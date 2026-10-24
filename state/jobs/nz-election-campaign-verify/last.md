Committed `eb27b19`, not pushed. Added `campaign_checks.py`, updated `verify.py`, and added `test_campaign_verify.py`. No UI changes.

Verification outputs:

- `uv run product/nz_election/pipeline/verify.py campaign --data <origin/data checkout>`: `PASS campaign`
- `uv run product/nz_election/pipeline/verify.py all`: ends with `PASS campaign` and `PASS all`
- `uv run --with pytest pytest -q product/nz_election/tests/test_campaign_verify.py`: `95 passed in 12.09s`
- `uv run --with pytest pytest -q product/nz_election`: `1 failed, 2116 passed, 2 errors in 606.70s`
- `bin/lint`: `lint ok (875 text files)`

All three browser failures reproduce on the unchanged base: Chromium `Permission denied (1100)`. Host rerun remains needed.

Full output and limitations are in uncommitted [last.md](last.md). Pollster records currently have no renderer; donation evidence relies on reviewed transcriptions.