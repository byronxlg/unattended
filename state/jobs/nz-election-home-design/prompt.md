# nz-election-home-design: home design round, issue #34 items 1 to 4 and 10

Build round in .worktrees/nz-election-home-design on change/nz-election-home-design from main
(6e5f3bf, after PR #38). Read first: issue #34's last two comments (`gh issue view 34 --comments`),
intent/nz-election/design-principles.md (binding), intent/nz-election/look-538.md (tokens, type),
the 538 reference https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/
if you can reach it (if not, the principles describe it), product/nz_election/pipeline/home.py,
market_panel.py, home_checks.py, product/nz_election/web/styles.css, and the existing SVG chart
code in build.py and social_page.py (reuse its style; no chart library, no bundler, no client JS
required to see a chart).

## Goal

The home reads like the 538 forecast page: one answer said in words, then chart after chart in a
narrow column. Today every module below the hero is a table, the hero leaves the reader to work
out whether 67 is a majority, and tables run 1280 px wide.

## Items (numbers from the review)

1. Graphics below the hero. Each data module gets one graphic as its primary form:
   - "How have the polls moved?": an inline SVG line chart of the party averages over time, one
     line per party at or above 5% or holding an electorate, party colours (principle 2: the
     party is the subject), direct labels at the line ends instead of a legend, a dashed 5% line.
   - Latest polls: a dot or bar chart per party (one row per party, the poll's share as a mark),
     not a table.
   - Closest electorates: a horizontal bar of each 2023 margin, names on the left in the text
     face, margin figure at the bar end.
   - Threshold watch and markets: your choice of graphic or a short list, but no wide table.
   Each chart keeps the existing accessible fallback (the same numbers in a visually hidden table
   or `aria-describedby` text, as the harness MISSING_SOURCE and axe checks expect), its one grey
   source footnote (principle 5), and one-click provenance. Numbers are unchanged: same data,
   new form.
2. The hero answers its own question in a sentence. Derive it from the seat numbers, not fixed
   copy: e.g. "On the current poll average, the governing parties would have exactly enough seats
   to govern" when Government equals the majority, "a majority of N" when above, "short by N"
   when below. The dek explains the majority figure (why 67 and not 61: House size including any
   overhang from the allocation). Check the House size and majority come from seats.py, and name
   the function in last.md.
3. Content width: cap the reading column at about 700 px on desktop (charts and text alike),
   centred, as 538 does; tables on other routes are untouched unless they share the home class.
4. Navigation: one nav row on desktop (fold the section links into the masthead row or drop them
   on home), nothing sticky that covers content (principle 8).
10. Election night module: give it a small graphic (e.g. a timeline from advance voting 26 Oct to
   the official result, today marked) or move it to the closing "More" list. Your call; say why.

## Constraints

- design-principles.md checks still hold: details 0, links under 60, "source" under 12, HTML under
  35 KB (inline SVG counts; keep paths lean, round coordinates to one decimal), at most six module
  h2 plus More, bloc colours only on bloc data.
- Harness geometry on the home must pass: HOME_MARKET_HEIGHT, SOURCE_NOTE_BELOW_FOLD, PAGE_OVERFLOW,
  SMALL_TARGET, HOME_ROW_KEYBOARD_FOCUS, AXE (including landmark-unique), measure_home. If an
  assertion pins a table structure that is now a chart (e.g. a row-link selector), move it to the
  equivalent chart element and name it in last.md with before and after; nothing weaker. Tests on
  main at 6e5f3bf are otherwise protected; your branch's own tests move with it.
- Add a geometry assertion that the seat bar's bounds sit inside the content column at 360, 390
  and 1280 (the PR #38 review nit), in the Chromium harness.
- Type and colour from look-538.md; no eyebrows, no all-caps labels, no arrows on links, no card
  borders or shadows, mono only for figures and timestamps.
- No new data source. Every number keeps its provenance path.

## Done

- `uv run --with pytest pytest -q product/nz_election` passes; `verify all` PASS; `bin/lint` ok.
- No-Chromium unit checks over the built HTML: each named module contains an `<svg>` with an
  accessible name; the hero sentence is right for three synthetic cases (equal, above, below);
  the column max-width rule exists. Each fails on 6e5f3bf.
- Commit in the worktree, do not push, never commit last.md. last.md: what changed per item, the
  measure_home numbers before and after, any moved assertion. The supervisor runs the Chromium
  harness and looks at home 360/390/1280; a fresh design review judges the screenshots against the
  538 reference before merge.
