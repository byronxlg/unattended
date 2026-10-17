Verdict: **request changes**

1. **Important** - `product/nz_election/pipeline/refresh.py:163`: Serializing `exc.locator` exposes raw wikitext for parser failures such as `invalid_attributes` and `unknown_template`. Reproduced a locator containing `data-sort-value BROKEN_WIKITEXT="2026-10-14" style="background:#E8E8E8;"`. Replace source-derived diagnostic text with a structural row/line locator before publication. Add a branch-owned regression test using malformed wikitext, asserting its contents never reach the status message, Actions log, or summary.

Verification:
- `bash evals/polls-date-exception-revision/check.sh`
  Output: `line 7: cannot create temp file for here document: Operation not permitted`
- `uv run --with pytest pytest -q product/nz_election/tests/test_date_exception_revision.py product/nz_election/tests/test_poll_parser.py product/nz_election/tests/test_refresh.py`
  Output: `Failed to initialize cache at /Users/byron/.cache/uv`; `Operation not permitted (os error 1)`
- `bin/lint`: same uv cache error.

Read-only Python probes: `PASS 28 read-only rejection probes`. Incident reproduction parsed 43 polls on HEAD; main raised `parse_drift invalid_dates` using identical fixture text and revision `9999999999`.

Existing tests at `8a5392d` and fixture bytes are unchanged. Full verification remains blocked by the read-only sandbox.