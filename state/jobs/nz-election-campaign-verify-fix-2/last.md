Committed `e905c50`; not pushed. Fixed campaign bundle/parser error boundaries and added marker regressions. `last.md` records both regressions failing on `7f027fb` and remains uncommitted.

Verification:

- Campaign tests: `148 passed`.
- Full product suite: `1 failed, 2172 passed, 2 errors`.
- `bin/lint`: `lint ok (875 text files)`.
- `verify.py all`: `PASS all`.
- `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py campaign`: `PASS campaign`.

Only known Chromium sandbox failures remain (`Permission denied (1100)`):

- `test_picker_chips_share_top_at_360`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

The requested `product/nz_election/verify.py` path does not exist; used the pipeline entrypoint above. Main-base tests were not edited.