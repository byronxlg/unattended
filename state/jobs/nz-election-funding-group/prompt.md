# nz-election-funding-group (build, UI)

Page plan: intent/nz-election/pages/funding.md
Design: product/nz_election/DESIGN.md (tokens and components; how it looks). The page plan sets what the page answers and in what order.

Branch change/nz-election-funding-group from origin/main (3f61409 or later). Your diff should touch funding/ only:
product/nz_election/pipeline/funding_page.py, its rules in web/styles.css (the funding block; leave header, nav and
night rules alone), its tests.

Read first: intent/nz-election/pages/funding.md (answer 5 and "Page order"), funding_page.py,
tests/test_funding_page.py, state/design-backlog.md (the 2026-10-27 lines that mention funding/).

Goal, from the design backlog (two items):
1. funding/ at 390 is about 21,000 px tall because every one of the 146 returns is listed in one column. Group the
   full list by party, as the page plan's answer 5 says: one group per party with an anchor `#<party_id>` (parties/
   already links to `funding/#<party_id>`; those links must still land), a short jump list of parties above the
   groups, and each group collapsed or summarised so the page at 390 is a few screens, not twenty. Every return
   stays on the page (no data removed, the 146-return count still visible), newest first inside a group, each row
   still linking its EC document. A party fragment in the URL must show that party's returns without extra clicks
   (open the matching group on load or with :target; works with JS off).
2. At 1280 the pace-of-arrival chart (answer 3) starts below the first screen. Tighten the order and density so at
   1280x800 the headline answer, chart 1 and the start of the pace chart or the top-ten table are on the first
   screen, keeping the page plan's order.

Constraints: tests check data, provenance, absence and accessibility, never markup, class names or byte counts.
Tests on main at the base sha are protected; your branch's own new tests move freely. No emojis, no em dashes.
Keep the existing EC credit line and provenance per return.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests -k "funding or design"` passes except Chromium launches
  your sandbox denies (list them by name; the supervisor runs them on the host).
- `bin/lint` prints `lint ok`.
- New tests that fail on the base: every party in the ranking has an element with id `<party_id>` on funding/ that
  contains that party's return count of document links; total document links still equal the return count.
- Report in last.md the funding/ page height at 390 and the y of the pace chart heading at 1280x800 if you can
  measure them (else say you could not; the supervisor measures on the host).
- Commit in the worktree, do not push. last.md: what changed per item, test output.
