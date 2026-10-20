Verdict: **accept**, with verification limits below.

- **Critical:** None found.
- **Important:** None found.
- **Nit:** None.

Confirmed:
- Descriptor failures now return `INVALID_ADVANCE`; three probes reproduce the original exceptions on `6bbc873`.
- Eight structural absence cases pass incorrectly on `6bbc873` and are rejected on HEAD.
- Per-row filtering preserves eligible observations. Disclosure appears above the chart/table and in methods (`campaign_page.py:36`, `:69`).
- No existing test was weakened or check moved. Count assertions increased to cover added captures/images.
- No new regression found in the inspected changes.

Read-only probe command: `PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<in-memory regression probes>'`
Output: `PASS read-only regression probes`

Limits: PR comments were unreachable; the engineer’s report was absent. Local pytest execution was blocked by cache permissions/missing pytest. Full-suite and screenshot results rely on the supplied host evidence; screenshots predate the fix. No files changed.