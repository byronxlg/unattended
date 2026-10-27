Verdict: **request changes**.

**Critical:** None.

**Important**

- `REVIEW.md:14`: Previous visual-verification finding remains unresolved. Available screenshots cover advance voting only. Before-advance, election-day, after-election, dark-mode and previous/reference comparisons remain missing. The reported 132 passing browser tests do not replace this review.

**Nit**

- `product/nz_election/tests/test_vote_page_sparse.py:33`: All 92 cases check semantic headings, without pinning classes or markup. They do not assert retained data, provenance or absent content; add those assertions to protect sparse rendering.
- `product/nz_election/web/styles.css:503`: Source credit remains distant from the countdown and timeline.
- `product/nz_election/web/styles.css:500`: Desktop help rows retain large gaps beneath shorter answers.
- `product/nz_election/web/styles.css:502`: Long deadlines compete visually with voting instructions.

Previous heading regression is fixed. Read-only Python probes covered **1,392 states** across four phases and the advance-opening boundary: **zero differences** against main in word/link/date inventories or question order; every state has exactly one h1. Empty pre-election input retains only comparison guidance, without snapshot credit or countdown.

Populated HTML is **byte-identical to pre-fix across six clocks**; CSS is unchanged by fix-1. Inspected both supplied screenshots. No pytest run or files changed.