Verdict: **request changes**

Critical: None.

Important:
- `product/nz_election/pipeline/verify.py:344`: Supplied-bundle validation escapes unsanitized. In-memory malformed-data probe produced `ValueError: INVALID_TIMESTAMP: envelope.data.RAW_UPSTREAM_SENTINEL.observed_at`. CLI validation at line 431 also bypasses campaign sanitization; line 494 forwards the message into exit text. Sanitize both paths and add regression coverage.
- `product/nz_election/pipeline/campaign_checks.py:94`: An unknown EC `p_no` raises a data-bearing `KeyError` before the owned invariant check. Changing a captured reference in memory produced `KeyError: 'RAW_UPSTREAM_SENTINEL'` through `check_snapshots()`. The CLI only catches `ValueError`, so this becomes a traceback. Normalize this failure to `CAMPAIGN_OFFICIAL_ERRORS`.

Nit: None.

Verification:
- Read-only Python probes confirmed both leaks.
- Funding-key and empty-heading regressions reject `eb27b19` and pass at `7f027fb`.
- Committed snapshot check: `146 donations, 20 records`.
- Existing `all` checks remain intact; no new network acquisition found.
- Full pytest rerun blocked: uv cache access denied by read-only sandbox; local `.venv` lacks pytest.