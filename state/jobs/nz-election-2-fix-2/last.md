Committed `33b906b`; not pushed. Existing tests unchanged.

- **1:** Successful bundles now sort by acquisition, then averages generation time; exact ties retain repository data. Latest attempt status merges independently. Proven by `test_equal_acquisition_keeps_latest_successful_generation`.
- **2:** Download summaries render timestamps in Pacific/Auckland; raw disclosures and manifests retain UTC. Proven by `test_download_retrieval_summary_is_auckland_and_records_stay_utc`.

Eight checks, all with `UV_OFFLINE=1`:

1. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   `Offline verification: immutable captures, not live data`
   `PASS refresh: polls bundle`
2. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`
   `PASS build: 6 routes`
3. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   `PASS build: 6 routes`
4. `uv run product/nz_election/pipeline/verify.py all`
   ```text
   PASS polls
   PASS thresholds
   PASS provenance
   PASS pipeline
   PASS all
   ```
5. `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
   `CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed`; `bootstrap_check_in ... Permission denied (1100)`.
6. `uv run --with pytest pytest -q`: `209 passed in 19.85s`, 0 skipped.
7. `bin/lint`: `lint ok (197 text files)`.
8. `git status --short`: empty after commit.

Departure: generation time uses the existing averages envelope; polls lacks that field. Open follow-up: supervisor runs screenshots on the host. Fresh visual verification remains blocked.