Committed `c8091e1`; not pushed. Campaign boundaries now catch `Exception`, preserve owned codes, and redact everything else. CLI uses the parsed check name regardless of argument order.

Verification:

- Campaign tests: `172 passed`.
- Full product suite: `1 failed, 2196 passed, 2 errors`.
- `bin/lint`: `lint ok (875 text files)`.
- `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py campaign`: `PASS campaign`.

Only known Chromium sandbox failures remain:

- `test_picker_chips_share_top_at_360`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

The requested `product/nz_election/verify.py` path does not exist. Main-base tests are unchanged. Uncommitted `last.md` records regressions failing on `e905c50`.