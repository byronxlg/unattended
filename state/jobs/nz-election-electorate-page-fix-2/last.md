Committed `099de3f`; not pushed.

Historical winner sentences and result bars now use readable names through the shared helper, preserving hyphens, macrons and mixed case.

- Tests: **1,979 passed, 1 failed, 2 errors**
- Chromium-launch failures only: `test_picker_chips_share_top_at_360`, `test_xml_python_browser_parity`, `test_replay_makes_no_official_feed_request`
- Populated verifier: **PASS all**
- Lint: **lint ok (664 text files)**
- New regression: fails on `b10fc2b`, passes on HEAD

Protected-main tests unchanged. `last.md` and artifacts remain uncommitted.