Committed `215baf9`. Added a home directory link when watch rows are unavailable. Harness and existing tests unchanged.

- Regression on `9a8aa1d`: 13 failed; fixed checks: 19 passed.
- `uv run --with pytest pytest -q`: 715 passed.
- `bin/lint`: lint ok.
- Verify: all PASS.
- Measurement PASS: details 0, links 37, source 7, HTML 10,685 bytes, h2 7. No-data fallback also passes.

Chromium remains sandbox-blocked; host harness verification is pending. Commands and outputs recorded in [last.md](last.md). No push; `last.md` and artifacts remain uncommitted.