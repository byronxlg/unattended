Committed `ff598b4`; not pushed.

Changed `social.py`, `test_social.py`, `verify.py`, and the runbook:
- Already-spent day exits 0, updates status, preserves data and ledger.
- No-prior-sample message corrected.
- Mid-run cap remains fatal.

Verification:
- `uv run --with pytest pytest -q product`: `1442 passed in 344.58s`
- Social tests, including two subsequently added cases: `43 passed`
- `bin/lint`: `lint ok (565 text files)`
- `PYTHONPATH=. uv run python -m product.nz_election.pipeline.verify all`: `PASS social`, `PASS all`

`last.md` contains the report and remains uncommitted. No open questions.