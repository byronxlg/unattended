Committed `866aad3`; not pushed. Worktree clean.

Changed only the authorized handover block in `result_states_browser.py`: pre-cutoff 503-to-settled handover preserves assertions; 27 November checks zero requests and the ended notice; rebuilt official HTML is checked.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night_stop_bootstrap.py product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_night_page.py
1 failed, 141 passed, 2 errors in 72.94s

bin/lint
lint ok (967 text files)
```

Chromium launch denied by sandbox (`Permission denied (1100)`), affecting:
- `test_result_states_browser`
- `test_xml_python_browser_parity`
- `test_replay_makes_no_official_feed_request`

Host browser rerun remains required. Report: [last.md](/tmp/nz-election-night-stop-fix2/last.md).