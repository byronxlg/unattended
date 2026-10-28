# Build: night/ replay date and electorate page polish (design backlog 28 Oct, items 2 and 3)

Page plans: intent/nz-election/pages/night.md and intent/nz-election/pages/electorate.md. Look: product/nz_election/DESIGN.md (tokens and components; use them, add none).

Goal, from the supervisor's design-loop critique of the deployed site on 28 Oct (state/design-backlog.md, top entry):

1. night/ replay (390 and 1280): under a 2023 replay that says "2023 final count" the page reads "Results last updated 10 November 2024 at 00:00." The date is wrong for the replay. Find where that time comes from (night page module and the replay/demo data path) and make the replay show the date its source actually records for the 2023 count (from the capture's provenance), or omit the line in replay mode when no such date exists. A live night keeps its real update time.
2. electorates/<slug>/ (seen on Nelson at 390): the h1 sits flush on "Who is standing in 2026?" with no space; give it the page's normal heading rhythm from DESIGN.md.
3. Same page: the 2023 result is stated twice ("General electorate ... won by 26 votes" in the intro and again under "Who won last time?"). Keep it once, in the section the page plan orders for it.
4. Same page: the locator hex map is all grey with one red cell and the caption "Highlighted seat". Caption it with the electorate's name (for example "Nelson on the electorate map") and keep the highlighted cell visible against the grey in light and dark.

Read first: the night page module and its replay data, the electorate page module, product/nz_election/DESIGN.md, the two page plans, REVIEW.md pass 4.

Constraints: tests check data, provenance, visible text order and absence; they do not pin markup, class names or byte counts. Tests on main at the base sha are contracts; where one pins the old replay date or the duplicate sentence, it moves with this change and you say which in last.md. Commit in the worktree, never push.

Definition of done:
- New tests: replay shows no 2024 date (or the source's 2023 date); an electorate page states the 2023 result once; the map caption names the electorate. Each fails on origin/main.
- `uv run --with pytest --with playwright pytest -q product/nz_election/tests -k "night or electorate or design"` passes (Chromium included).
- `bin/lint` prints lint ok.
- last.md lists what changed, the commands and their output lines, and any moved contract.
