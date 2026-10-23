**Verdict: request changes.**

**Critical:** None found.

**Important**

- [snapshot_views.py:103](product/nz_election/pipeline/snapshot_views.py#L103): Electorate maps return before rendering the exact-value table and legend. Their `role="img"` exposes a generic label; descendant `<title>` elements do not provide an equivalent to the 71 coloured, shaded results. Retain an accessible table on electorate pages too.

- [snapshot_views.py:115](product/nz_election/pipeline/snapshot_views.py#L115): The map’s Methods target credits only Stats NZ geometry, although colours and margins derive from EC results and the Port Waikato snapshot. Link those result sources and licences from this target. Separately, [electorate_pages.py:104](product/nz_election/pipeline/electorate_pages.py#L104) renders Port Waikato party votes referencing `source-baseline-2023`, which resolves to an empty span rather than provenance.

- [home.py:292](product/nz_election/pipeline/home.py#L292): An empty-data render still emits “Closest on unchanged boundaries” with no rows. The absent-text gate passes this empty content. [build.py:381](product/nz_election/pipeline/build.py#L381) also retains “Not reported” for absent sample sizes. Omit both and test semantic absence alongside banned words.

**Nit**

- [electorate_pages.py:73](product/nz_election/pipeline/electorate_pages.py#L73): Port Waikato still says “Nineteen electorates are unchanged.” The fix handles only one exact wording; make this seat-specific or omit it.

Visually, the hero meets the reference’s clear-answer hierarchy and restrained colour. Reviewed home at 1280/390/360, Nelson at 1280/390, and Port Waikato at 390. No visible home overflow at 360; the supplied manifest records Nelson at 1,523 px tall.

Read-only checks against the supplied build returned `absent gate: 79 routes PASS` and `role-img gate: PASS`. The empty-heading and provenance probes reproduced the findings above. Budget increases were documented with reasons in the engineer’s recorded report; I found no additional weakening of the browser accessibility or overflow checks.

Full pytest/browser runs were not repeated. PR comments remained inaccessible through CLI and connector; the archived reference also failed to load. No files changed.