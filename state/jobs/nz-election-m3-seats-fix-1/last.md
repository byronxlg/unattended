Committed `ec9d3fb`; not pushed. Fixed clipping, named ties with margin 0, table selection targets, and the runbook.

Verification:
- New regressions: 10 failed on `467512b`, all pass now.
- Focused suite: 50 passed.
- Product suite: 1883 passed; Chromium launch errors only in `test_xml_python_browser_parity` and `test_replay_makes_no_official_feed_request`.
- Verifier: `PASS all`
- Lint: `lint ok (621 text files)`

Per-item evidence is in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-m3-seats/last.md). Browser geometry checks remain blocked by the sandbox.