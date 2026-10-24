Committed `7943528`. Not pushed; `last.md` remains uncommitted.

- `publish.py`: disables automatic GC, maintenance, and GC detachment immediately after init.
- Added `test_publish_cleanup.py`; existing tests unchanged.

Verification:
- `uv run --with pytest pytest -q product/nz_election/tests -k publish`: **5 of 5 passed**, each `33 passed, 1987 deselected`.
- `uv run --with pytest pytest -q product`: `1 failed, 2017 passed, 2 errors in 642.18s`.
- `bin/lint`: `lint ok (827 text files)`.

All three full-suite issues were Chromium sandbox launch denials:
- `test_picker_chips_share_top_at_360`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

Details recorded in `last.md`. No open questions.