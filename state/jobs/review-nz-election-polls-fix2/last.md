Verdict: **accept**.

- **Critical:** none.
- **Important:** none.
- **Nit:** none.

Checked:
- `product/nz_election/pipeline/poll_parser.py:205`: canonical sort dates accepted through end +7 days; earlier, malformed and out-of-bound dates raise `invalid_dates`.
- `product/nz_election/pipeline/refresh.py:163`: public status uses structural `public_locator`. Log and summary reuse that sanitized message.
- `product/nz_election/tests/test_date_exception_revision.py:43`: all six authorized cases retain failure checks and add explicit release-date fallback assertions. No unauthorized test weakening in the requested diff.

Verification:
```text
Focused pytest: 49 passed, 9 deselected in 3.31s
Eval on fe698de: FAIL parse_drift invalid_dates table:15/row:2
Eval on 03a72cf: PASS release-date row parsed
Existing eval: PASS exception row parsed on revision 9999999999
Live capture: rows=44, Freshwater 2026-10-19 exists=True
```

Eval Python payloads ran in memory against each revision. Filesystem-writing integration tests were excluded under read-only access; public output paths were inspected. The claimed full-suite and lint results were not independently rerun.