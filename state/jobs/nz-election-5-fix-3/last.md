Committed `ec78040`; not pushed.

Registry binding: `daily_refresh.py` records the canonical registry payload’s SHA-256 in `input_hashes["electorates.data"]`. `export.py::validate_bundle` checks it snapshot-locally and raises `GEOGRAPHY_REGISTRY_HASH_MISMATCH`.

Added tests:

- `test_geography_registry_bound_after_inventory_regeneration`
- `test_geography_registry_binding_rejects_malformed_hash`
- `test_svg_budget_css_references`
- `test_svg_budget_css_rejects_unsafe_and_missing_assets`
- `test_svg_budget_current_page_unchanged`

Electorates SVG total: **284,316 bytes before and after**. Current CSS adds no SVG file downloads.

```text
uv run --with pytest pytest -q product/nz_election/tests
222 passed in 45.74s

uv run --with pytest pytest -q
306 passed in 45.68s

git diff ba8914b --stat -- product/nz_election/tests
3 files changed, 116 insertions(+)

python3 product/nz_election/pipeline/verify.py all
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

The previous 295 count covered the full repository. Fixtures, budgets, existing assertions, and increment 4 files remain unchanged.