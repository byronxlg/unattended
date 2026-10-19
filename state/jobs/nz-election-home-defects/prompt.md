# nz-election-home-defects: six defects on the live home (issue #34, operator design review 2026-10-19 01:50Z)

Build round in .worktrees/nz-election-home-defects on change/nz-election-home-defects from main
(after PR #37). Read first: issue #34's last comment (`gh issue view 34 --comments`),
intent/nz-election/design-principles.md, product/nz_election/pipeline/home.py, market_panel.py,
home_checks.py, market_budget_checks.py, and product/nz_election/tests/screenshots.py.

## Defects (numbers from the review)

5. Threshold watch: Opportunity 6.2% sits in a column headed "Below 5%" with value "Needs 5%".
   Find whether the figure, the grouping or the label is wrong; fix the cause, not the text.
6. Latest polls shows only National, Labour, Green. Show every party at or above the 5% threshold
   or holding an electorate in the poll (ACT and NZ First included), same order as the trend table.
7. Pollster names render lowercase in mono ("verian", "anacta", "curia"). Use display names
   ("1 News-Verian", "Talbot Mills", ...) from the poll source in the text face.
8. Closest electorates: margin figures sit a line above their electorate names. Align on one
   baseline; names in the text face, links styled like the other home row links, not code.
9. Prediction markets: each row says the question the market asks in plain words (for example
   "Will Christopher Luxon be the next Prime Minister?") before its price; drop the
   "Highest Yes price per event" heading for a reader-facing one.
11. Phone 390 and 360: the seat bar runs past the text column to the screen edge; it sits inside
   the column at every width.

## Constraints

- Geometry assertions the harness makes on the home, all must still pass: HOME_MARKET_HEIGHT
  (market_checks.py), SOURCE_NOTE_BELOW_FOLD (screenshots.py ~221), PAGE_OVERFLOW, SMALL_TARGET,
  HOME_ROW_KEYBOARD_FOCUS, AXE landmark-unique, measure_home (details 0, h2 count, byte budget).
  List each one you touched in last.md with its before and after number.
- Tests on main at the base sha are protected except where an assertion pins the defective text
  (for example "Below 5%" or "Highest Yes price per event"); name each one you move and why. Your
  branch's own tests move with it. Nothing weaker.
- Every number keeps its provenance path. No new data source.

## Done

- `uv run --with pytest pytest -q product/nz_election` passes; `verify all` PASS; `bin/lint` ok.
- A no-Chromium check per defect that fails on the base sha and passes on HEAD (5, 6, 7, 9 at
  least as unit tests over the built HTML).
- Commit in the worktree, do not push. last.md: what each defect was caused by, the checks, and
  the geometry table. The supervisor runs the Chromium harness and looks at home 360/390/1280.
