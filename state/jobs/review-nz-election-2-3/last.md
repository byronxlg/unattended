- **Important** - `product/nz_election/pipeline/publish.py:63`: String comparison can discard the latest failure, contradicting the runbook’s latest-attempt invariant.
  **Reproduction:** Equal successful bundles; repository attempt `2026-10-17T01:00:00Z`, incoming failure `2026-10-17T01:00:00.100000Z`. Python reproduction returned `keep_data=True, keep_status=True`, triggering `older-run-retained` and losing the newer failure.
  **Fix:** Compare parsed, timezone-aware attempt timestamps.

- **Important** - `product/nz_election/pipeline/publish.py:29` and `product/nz_election/pipeline/build.py:56`: Accepted timezone-less timestamps cause publication errors and host-dependent display.
  **Reproduction:** `generated_at="2026-10-17T01:00:00"` passes envelope validation, but comparison against an aware generation raises `TypeError: can't compare offset-naive and offset-aware datetimes`. Rendering that timestamp produces **2 pm NZDT** on a UTC host and **1 am NZDT** on an Auckland host.
  **Fix:** Require timezone-aware operational timestamps at validation, normalize to UTC, and preserve date-only poll observations.

Review checks: both added tests would fail on `2daec23`: publication replaces the newer generation; downloads lacks the Auckland retrieval label. Test diff: **66 additions, zero deletions**. No-poll ordering is safe; partial poll bundles are rejected before ordering; retained generations survive later failed attempts with canonical timestamps.

Both downloads screenshots inspected. No additional visual finding; neither exposes a non-null retrieval timestamp. Python checks confirmed NZST/NZDT conversion for explicit UTC offsets and unchanged date-only observation labels. Full suite not rerun in the read-only sandbox.

Important findings: 2