Committed `637a173`. Not pushed.

Reduced repeated seat/SVG markup in three renderers, home template and CSS; added byte regression tests. Home: **68,868 → 59,724 bytes**. Answers, order and budgets preserved.

Verification:

```text
bash evals/pages-home-bytes-live/check.sh
PASS all
PASS home under budget on data d7b8db903ba4e354f995afc9bd53d12f9d992139

uv run --with pytest pytest -q product
1 failed, 1960 passed, 2 errors in 616.07s (0:10:16)

bin/lint
lint ok (664 text files)
```

All three test exceptions are Chromium sandbox launch failures:
- `test_picker_chips_share_top_at_360`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

Screenshots were blocked by the same launch error. `last.md` records measurements and limitations; it and `artifacts/` remain uncommitted. No open questions.