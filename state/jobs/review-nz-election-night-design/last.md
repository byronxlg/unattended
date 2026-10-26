Verdict: **request changes**.

**Critical**
- None found.

**Important**
- `product/nz_election/pipeline/night_page.py:79`: Eight expanded majority cards push electorate search beyond two phone screens. The supplied 390 screenshot fails `pages/night.md`’s “find their electorate in one scroll” requirement. Collapse combinations or provide search immediately after the hero.
- `product/nz_election/pipeline/night_electorates.py:84`: Shared-map migration retains overlapping electorate cells: Invercargill/Rongotai, Mana/Southland, New Lynn/Taieri, Bay of Plenty/Dunedin. Later polygons conceal earlier leaders. This predates the PR, but remains a pass-4 defect. Place historic extras outside occupied coordinates.

**Nit**
- `product/nz_election/pipeline/home_graphics.py:81`: The majority marker crosses near-black NZ First dots and becomes difficult to distinguish in the replay screenshot. Add a contrasting underlay. This is an existing shared-component weakness.

Verification:
- In-memory parser/render probes: `house 122; sum seats 122; dots 122; parser agreement True`; blocs 67/55, majority 62.
- Source records unchanged. Before-results order, s197 notice and aria-live retained. Removal selectors exclude the results container.
- Changed assertions preserve substantive checks; no weakening found.
- `node --test product/nz_election/tests/night_scheduler.test.mjs`: **1 passed, 0 failed**.
- Inspected all four supplied screenshots. No pytest or file changes.
- Remaining verification gaps: 360px overflow, dark mode, previous-version/reference comparisons, and browser execution of live removal. Supplied screenshots alone cannot establish these.