Committed `b5b0b9d`; not pushed.

Spent-day status now has `error_code=null`, preserving its message and last-success timestamp. Mid-run caps remain fatal. Updated `social.py`, tests, and runbook; publisher checks unchanged.

Verification:
- New publisher test before: `2 failed, 2 passed`
- After: `4 passed`
- `uv run --with pytest pytest -q product/nz_election`: `1448 passed in 345.45s`
- `bin/lint`: `lint ok (566 text files)`
- Verifier: `PASS social`, `PASS all`

`last.md` records the evidence and remains uncommitted. No open questions.