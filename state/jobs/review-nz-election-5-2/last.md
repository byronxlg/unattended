- **Important** - `product/nz_election/pipeline/export.py:284`: Registry contents are no longer bound to their recorded input hash. The inventory verifies output bytes, while geography validation only compares IDs/names. Reproduction: change `electorates.data[0].boundary_note`, regenerate its JSON/CSV and inventory, leave `input_hashes` unchanged. In-memory probe: `ACCEPTED`. The new regression test catches only an outdated inventory. Fix: retain a verifiable snapshot-local registry hash and validate it without consulting checkout configuration.

- **Important** - `product/nz_election/tests/svg_budget.py:26`: CSS SVG references escape the page budget, including inline styles, `<style>` blocks and linked stylesheets. Reproduction: `svg_page_bytes('<div style="background-image:url(../maps/general.svg)"></div>', site)` returns `0`. Fix: collect CSS `url(...)` dependencies, resolve them relative to their document or stylesheet, and include their SVG bytes.

Other checks: daily production retains its current-registry gate; hourly refresh retains geography; publication still validates incoming and merged bundles. Mixed-generation probe: `MIXED_GEOGRAPHY_GENERATION`.

The test diff is not literally additions-only: three lines are replaced, including the manifest-count assertion, 25 to 27. No budget constants changed. Duplicate-map probe: `568632`, exceeding `300000`.

All 297 fold entries match Python; Node parity passes. ASCII and macron queries normalize consistently with directory keys. Companion notes document derivation; both one-byte mutation probes return `CAPTURE_HASH_MISMATCH`.

Read-only probes used `python3 -B -c`; `uv run` was blocked by temporary-file creation. Full suite not rerun.

Important findings: 2