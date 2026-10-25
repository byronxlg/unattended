Verdict: **request changes**

Critical: None.

Important:

- `product/nz_election/pipeline/verify.py:434-446`: Missing-family detection precedes bundle validation only for explicit `night --data`. If `night/index.json` is lost but remains in the manifest, bundle validation fails before the required-family guard. Consequently, `all --require night,waterfall` reports `CAMPAIGN_DATA`; explicit `waterfall` reports `INVALID_INVENTORY`, instead of `MISSING_NIGHT_FAMILY`. Move the required-night presence check ahead of bundle/site validation, using the resolved `night_data` path. Isolated CLI probes reproduced this inconsistent error handling. Exits remain nonzero.

Nit: None.

Read-only probes against committed `617dd80` confirmed:

- Otherwise-valid absent families fail for required checks through both `--data` and `--site`.
- Optional families emit both SKIP lines.
- `thresholds --require polls` invokes both checks.
- Unknown requirements fail; aggregate errors retain campaign redaction.
- No existing tests changed.

No pytest run. Probes mocked filesystem/setup operations; they were not end-to-end validation.