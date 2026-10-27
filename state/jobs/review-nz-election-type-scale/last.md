**Verdict: request changes.**

**Critical:** None found.

**Important**

- `product/nz_election/web/styles.css:425` and `:387`: SVG labels still fall below DESIGN.md’s 12 px rendered minimum at 360 px. With 16 px gutters, the map’s 466-unit viewBox scales its 16 px labels to **11.26 px**; the narrow trend’s 360-unit viewBox scales its 12 px labels to **10.93 px**. Adjust coordinate font sizes or narrow layouts. The trend issue predates this diff but remains within the explicitly requested scaling check.

**Nit:** None.

Funding provenance checks passed for all seven parties: totals, counts, threshold before total, adjacent caveat, EC link. Test changes affect literal sizing assertions only; wrapping, data, provenance and accessibility checks remain.

Read-only Python probes reported:

```text
PASS funding: 7 parties, sums/counts/threshold order/caveat/EC link
PASS CSS: no non-token font-size declarations
360px viewport: hemicycle label = 12.30px
360px viewport: map label = 11.26px
360px viewport: trend narrow label = 10.93px
```

Inspected all 12 supplied PNGs. No obvious overlap in their visible areas. Pass 4 remains incomplete: these are viewport captures, without dark-mode, previous-version or reference comparisons. They do not establish full-page overflow safety at 360 px. On parties/mobile, leader and polling are visible, but policy and governing-partner answers remain below the captured viewport.

No pytest run; no files changed.