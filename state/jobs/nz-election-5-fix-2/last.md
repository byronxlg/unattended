Committed `ba8914b`; not pushed.

1. **Snapshot retention:** `pipeline/export.py`, `tests/test_contracts.py`. Removed checkout-config comparisons from snapshot validation; retained inventory hash checks and producer validation. Regressions:
   - `test_last_good_geography_survives_config_correction`
   - `test_geography_snapshot_hash_mismatch_rejected`
   - `test_geography_producer_checks_current_registry`

2. **Reference pinning:** `fixtures/manifest.json`, `tests/test_geojson.py`, `tests/test_contracts.py`. Companions now load through `captures()`; bytes unchanged. Manifest count **25 → 27**. Regression: `test_reference_capture_hash_pinned`, parametrized for both companions.

3. **Rendered SVG budget:** `tests/test_geography.py`, new `tests/svg_budget.py`. Extended `test_svg_page_budget` to measure built HTML and linked SVG files; preserved outline checks. Regression: `test_svg_budget_counts_duplicate_and_linked_maps`.

4. **Search parity:** `pipeline/geography.py`, `web/electorates.mjs`, `tests/test_geography.py`. Aligned case folding, mark removal and whitespace handling. Regression: `test_search_key_python_js_parity`, covering 71 names and Unicode probes.

```text
uv run --with pytest pytest -q
295 passed in 40.47s

uv run python product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS all

bin/lint
lint ok (254 text files)
```

Departures: none. Increment 4 files untouched.