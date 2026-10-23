**Verdict: request changes.**

**Critical:** None found.

**Important:**

- `product/nz_election/pipeline/snapshots.py:450`: Licence validation accepts any globally recognised licence. Direct probes accepted `CC0` and `Public domain` for both new snapshot types, contrary to their EC copyright and Policy.nz link-only provenance. Enforce source-specific licences. Add tests for recognised-but-wrong licences and missing `source_url`; current tests cover neither.
- `product/nz_election/pipeline/home_charts.py:113`: Home/polls changes extend beyond party links. Minimum trend-label spacing doubles from 22 to 44 px, changing connector positions and potentially chart height. Revert or explicitly approve and visually verify this layout change.

**Nit:** None.

Verification:

- Browserless outline: passed all 81 existing populated routes. Current party markup passes; `bbbb576` reproduces `FAIL HEADING_OUTLINE`.
- Committed provenance cases run with in-memory files: `PASS 16 committed provenance cases`.
- Focused pytest with capture/cache disabled: `7 passed, 1 deselected in 0.06s`.
- Picker test covers 360 and 390; CSS explicitly prevents wrapping. Browser execution remains unverified.
- Existing main assertions retain their checks; route inventories increase to 81.

Review limitations: No review screenshots were available, so the required screenshot-first question and graphic tests remain unverified. Prior PR comments were inaccessible through both `gh` and the connector. Standard `uv` verification was blocked by read-only cache permissions. No files changed.