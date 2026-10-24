Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/pipeline/campaign_checks.py:33` and `verify.py:494`: Exception allowlist leaves parser failures unredacted. Injecting `RuntimeError`, `AssertionError` or `EOFError` containing `RAW_UPSTREAM_SENTINEL` into `gzip.decompress` escapes the campaign guard; the CLI also lets these exceptions reach tracebacks unchanged. Catch ordinary `Exception` at the reporting boundary and translate to owned codes.

- `product/nz_election/pipeline/verify.py:495`: Redaction uses `sys.argv[1]`, rather than the parsed check. Valid option-first invocations bypass campaign/all sanitization. Probing actual `main()` with an injected read failure produced:
  ```text
  actual main --site /supplied campaign: FAIL --site: RAW_UPSTREAM_SENTINEL
  actual main --site /supplied all: FAIL --site: RAW_UPSTREAM_SENTINEL
  ```
  Use the parsed check consistently.

Nit: None.

Read-only probes used `PYTHONDONTWRITEBYTECODE=1 python3 -B -c ...`; no pytest or file changes. Additional output:
```text
check_snapshots: PASS
unknown EC p_no: CampaignError CAMPAIGN_OFFICIAL_ERRORS marker=False
bundle ValueError: CampaignError CAMPAIGN_DATA marker=False
```

The two previously reported paths are closed for those exceptions. No existing check was loosened or removed from `all`.