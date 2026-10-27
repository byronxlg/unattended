# nz-election-funding-nits (build, UI)

Page plan: intent/nz-election/pages/funding.md
Design: product/nz_election/DESIGN.md (tokens and components; how it looks). The page plan sets what the page answers and in what order.

Branch change/nz-election-funding-nits stacks on change/nz-election-parties-credit (PR #107), which stacks on
change/nz-election-funding-page (PR #105). Your diff should touch funding/ only: funding_page.py, its styles block in
web/styles.css (around the funding rules, lines ~520-540; leave the header/nav rules alone, another branch is
changing them), its tests, and data handling for donations if item 1 needs it.

Read first: intent/nz-election/pages/funding.md, product/nz_election/pipeline/funding_page.py,
product/nz_election/tests/test_funding_page.py, state/design-backlog.md (the 08:30Z, 08:20Z and 07:55Z funding lines).

Fix, from the backlog:
1. "Te Tai Tokerau" appears as a party row in the funding ranking. Find which return produces it (probably an
   electorate candidate return or a mis-parsed party name in snapshots/donations.json) and make the ranking hold
   parties only; if it is a real non-party return, say where it goes instead. Keep the 146-return count invariant
   and the per-return provenance.
2. Party totals in the top line and the ranking in whole dollars (NZD 2,394,410), not cents; detail tables may keep cents.
3. At 390, the donor tables scroll sideways to compare donor, amount and date. Make each row readable at 390
   without sideways scroll (for example stack donor over amount and date), keeping a real table with headers for
   assistive tech.
4. At 1280, the timeline (pace of arrival) starts below the first screen; and at 390 the party ranking fills the
   first screen so the biggest-donor answer gets no invitation. Tighten the order and density so the first screen
   at 390 shows the headline answer, the top of the ranking and a visible pointer to the biggest donors, per the
   page plan's order.

Constraints: tests check data, provenance, absence and accessibility, never markup, class names or byte counts.
Tests on main at its current sha are protected except where a funding assertion pins the cents format of item 2
(that one moves with the change; say so in last.md). No emojis, no em dashes.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests -k "funding or design"` passes except Chromium launches
  your sandbox denies (list them; the supervisor runs them on the host).
- `bin/lint` prints `lint ok`.
- A new test that fails on the base (fa33005) for item 1 (no non-party row in the ranking) and item 2.
- Commit in the worktree, do not push. last.md: what changed per item, what Te Tai Tokerau was, test output.
