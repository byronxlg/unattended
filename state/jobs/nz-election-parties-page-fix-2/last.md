Committed `367556d`. Fixed first-party subheading levels and preserved styling/order. Added browser-free outline coverage for all 81 routes.

- Regression test: fails on `bbbb576`; passes on `367556d`.
- Populated build: `PASS build: 81 routes`.
- Populated verifier: `PASS all`.
- Lint: `lint ok (622 text files)`.
- Pytest: `1859 passed, 1 failed, 2 errors`.

Only exceptions were sandbox Chromium launch failures (`Permission denied (1100)`):

- `test_picker_chips_share_top_at_360`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

Evidence recorded in uncommitted `last.md`. No push.