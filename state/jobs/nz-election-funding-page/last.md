Committed `1e6cdc5` on `change/nz-election-funding-page`. Not pushed.

Added funding renderer, SVG charts, all 146 document links, home/party links, navigation changes and semantic tests. Updated route contracts to 82 pages.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests
17 failed, 3057 passed, 2 errors in 1022.02s (0:17:02)

bin/lint
lint ok (1174 text files)
```

All failures/errors are Chromium launches denied by the sandbox:

- `test_phone_rendered_type_and_targets[map, trend, header]`
- `test_electorate_phone_browser[fold, empty]`
- `test_browser_handover[absent, zero, complete, recovery]`
- `test_retirement_browser[cached-after-stop, waiting-after-stop]`
- `test_browser_checks[probe, rehearse, faults]`
- `test_night_design_browser`
- `test_picker_chips_share_top_at_360`
- `test_result_states_browser`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

Open: 390/1280 screenshots and visual review remain blocked. Full results and contract changes are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-funding-page/last.md), uncommitted as requested.