Verdict: **accept**.

- **Critical:** None.
- **Important:** None found.
- **Nit:** None.

Cap, reservations, and pre-request limits remain intact. Validator enforces canonical ordered windows and consistent counts. Partial coverage is explicit in provenance, status, and page text. Zero-window failure retains prior data; retry diagnostics contain only safe fields.

Read-only verification:
- Baseline replay: 23 windows, 230 classifications, 24 requests; rejected with `INVALID_SOCIAL_PROVENANCE`.
- HEAD replay: same sample validates; spent = 7,560.
- `PASS: 42 malformed-window validator probes; gapped provenance; fresh/stale POC, home caption and notice coverage`

Full eval and pytest were blocked by uv cache permissions; end-to-end publication and screenshots remain unverified. No files changed.