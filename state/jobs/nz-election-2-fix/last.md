Committed `2daec23`; not pushed. Existing tests remain unchanged.

Fixes and new regression tests in `test_increment_two_regressions.py`:

- **0:** Leased pushes compare remote SHAs before retrying. Tests: `test_ci_incorrect_old_value_retries`, `test_push_failure_without_ref_movement_is_fatal`.
- **1:** Exact integer scaling, including refresh normalization. Test: `test_large_scale_never_rounds_into_qualification`.
- **2:** Shared threshold helper filters by average poll IDs. Test: `test_threshold_uses_only_average_ids_including_missing_coverage`.
- **3:** Latest failure status merges independently of retained data. Test: `test_later_failure_merges_status_without_replacing_newer_data`.
- **4:** Documented output allowlist protects blog directories and symlink aliases. Test: `test_blog_output_allowlist_preserves_every_sibling`.
- **5:** Downloads show complete provenance, run links and unavailable values. Test: `test_downloads_render_each_manifest_record_and_run`.
- **6:** Borderless, staggered labels connect to segment positions; fitting counts remain inside. Test: `test_strip_labels_have_spatial_anchors_and_staggered_lanes`.

All commands ran with `UV_OFFLINE=1`:

1. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   Output: `Offline verification: immutable captures, not live data`; `PASS refresh: polls bundle`
2. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`
   Output: `PASS build: 6 routes`
3. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   Output: `PASS build: 6 routes`
4. `uv run product/nz_election/pipeline/verify.py all`
   Output:
   ```text
   PASS polls
   PASS thresholds
   PASS provenance
   PASS pipeline
   PASS all
   ```
5. `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
   Error: `CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed`; `bootstrap_check_in ... Permission denied (1100)`.
6. `uv run --with pytest pytest -q`: `207 passed in 17.58s`, 0 skipped.
7. `bin/lint`: `lint ok (196 text files)`.
8. `git status --short`: empty after commit.

Inspected earlier phone and desktop screenshots: detached tiles confirmed. Fresh screenshots remain blocked, so the new layout is not visually verified. Supervisor follow-up: run screenshots on the host and inspect both widths. No other departures or open questions.