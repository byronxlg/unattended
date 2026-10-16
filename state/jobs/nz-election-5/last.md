Committed `6338a9d` and `a38e369`; not pushed. Built geography validation/reference tooling, atomic daily bundles, SVG maps, directory/search, and tests. Enforcers documented in `product/nz_election/geography.md`.

Registry: **71 rows**. SVG: **284,316 bytes** index; **15,339 bytes** largest outline. Māori capture budget: **110,196 bytes**. Hourly parity: **11 files byte-identical**.

Verification:
```text
uv run product/nz_election/pipeline/verify.py geography
PASS geography: 64 general, 7 Māori
uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS all
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
Offline verification: immutable captures, not live data
PASS refresh: polls bundle
uv run product/nz_election/pipeline/daily_refresh.py --out artifacts/nz-election/data
PASS refresh: daily bundles
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election
PASS build: 6 routes
uv run --with pytest pytest -q
1 failed, 287 passed in 36.60s
bin/lint
product/nz_election/fixtures/party-identity/grn.html:6071: em dash
product/nz_election/fixtures/party-identity/opp.html:303: emoji
uv run product/nz_election/pipeline/geo_reference.py --help
usage: geo_reference.py [-h] --out OUT input
```
Expected failure: `test_reference_capture_required`; independent reference companions await host generation. Immutable captures causing lint failures remain untouched.

`uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots` failed at Chromium launch: sandbox permission denied. Host inspection remains required; configured total: **24 images**.

Departures:
- Restored missing increment 4 product files from locally available `361760c`.
- Exported non-coordinate numeric geometry properties as decimal strings.
- Updated obsolete bootstrap assertion to the explicit hourly file set. `test_capture_manifest` changed only **11 → 25**.