Verdict: **request changes**.

- **Important**: [advance_acceptance.py:96](product/nz_election/pipeline/advance_acceptance.py:96) matches a numeric suffix rather than the complete displayed count. Both pages can say `-175,748 advance votes reported through 27 October.` and acceptance passes against registered cumulative count `175748`. Validate the complete count token, including rejecting signs and decimal prefixes, and add both-route regressions.

Read-only, in-memory probe of `check()` with mocked bundle/filesystem reads:
```text
Registered latest: 2026-10-27 175748
visible: PASS
chart-data: ADVANCE_NOT_PUBLISHED
negative count: PASS
decimal count: PASS
```

Fix-2 closes the reported `.chart-data` defect. No additional findings in default verification or runbook commands.

Attempted verification:
```text
uv run --offline --with pytest pytest -q -p no:cacheprovider product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py product/nz_election/tests/test_harden*.py
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: ... Operation not permitted (os error 1)
```

Full pytest results remain supervisor-provided evidence. No files changed.