Verdict: **request changes**

**Critical:** None found.

**Important:**
- `product/nz_election/pipeline/campaign_checks.py:183`: Error messages expose upstream text, violating the explicit sanitized-message requirement. Reproduced with `<section><h2>RAW_UPSTREAM_SENTINEL</h2></section>`:
  ```text
  CAMPAIGN_ABSENT: EMPTY_MODULE: RAW_UPSTREAM_SENTINEL
  ```
  Replace forwarded exception text with fixed descriptions. Audit similar interpolation at lines 42, 58, 94, 152 and 168; add tests asserting input text never appears in failures.

**Nit:** None.

Verification: direct read-only execution of `check_snapshots()` and `check_markup(page(...))` returned:
```text
PASS snapshots and markup: 146 donations, 20 poll records, 0.23s
```

Existing checks retain their order; campaign is appended. Full tests and workflow timing were not independently verified: `uv run` cannot create temporary files under this sandbox, and `.venv` lacks pytest. No files changed.