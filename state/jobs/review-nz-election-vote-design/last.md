Verdict: **request changes**.

**Critical:** None.

**Important**

- `product/nz_election/pipeline/vote_page.py:52`: Moving the timeline outside `places` breaks sparse-data heading parity. Reproduce with `rows` containing only `advance-opens` or `advance-closes`: the timeline remains, but “Where can I vote, and when?” disappears and there is **no h1**. Previously both existed. Preserve a meaningful heading when dates are the only available answer.
- `REVIEW.md:14`: Visual verification remains incomplete. Supplied screenshots cover advance voting only; before, election-day, after, dark mode, and previous/reference comparisons are missing.

**Nit: three weakest visual elements**

- `product/nz_election/web/styles.css:503`: Source credit is far below the countdown and timeline; a nearby source link would make provenance easier to discover.
- `product/nz_election/web/styles.css:500`: Desktop help rows leave substantial empty space beneath shorter answers.
- `product/nz_election/web/styles.css:502`: Long help deadlines have the same visual weight as instructions, making phone scanning harder.

Read-only probes covered **42 variants × four phases**. Full snapshots, empty input and single-record omissions preserve words and links; sparse variants expose the heading regression above. Default `home.section()` output remained byte-identical in four probes. No tests or contracts changed.

The supplied phone screenshot satisfies first-three-answer placement. CSS retains 44px targets, visible focus and reduced-motion support; checked text tokens exceed 4.5:1 in both themes. DESIGN.md matches the implemented layout.

Existing tests **do pin literal markup**, including `test_vote_page.py:77`; this PR preserves those selectors. No pytest run.