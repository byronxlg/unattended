# NZ election: design system

Living document. Written 2026-10-26 with the redesign (PR "Redesign: design system, home and
polls"), after Byron's 2026-10-20 ask for "a fully redesigned website that I would be proud to call
mine". It replaces the measure tables in `intent/nz-election/design-principles.md` and the tokens
in `look-538.md`; the reader-first page plans still decide what a page says, this decides how it
looks. Change this file in the same PR as any change to tokens or components.

The bar: put a page beside the 538 2024 forecast or NBC's midterms hub at the same width, and it
should look like it belongs in that company. Measures (bytes, link counts, heading counts) are not
the bar; the screenshot is.

## Tokens (`web/styles.css`, `:root`)

- Ground `--paper`, panel `--wash`, ink `--ink`, secondary text `--soft`, captions `--grey`,
  rules `--rule` and `--hair`. Masthead `--mast` with `--accent` for the current tab.
- Parties are tokens, never literals: `--p-nat --p-lab --p-grn --p-act --p-nzf --p-tpm --p-opp
  --p-other`, each with a dark-mode value. Python writes `home_graphics.pc(party)`, which returns
  `var(--p-xxx)`; put it in `style=""` (fill, stroke, background, `--c`). Display colours are
  editorial: they follow NZ media convention (ACT yellow, NZ First black, Te Pati Maori maroon)
  so that no two parties read alike on a chart; the sampled brand colours stay in
  `config/party-colours.json` as evidence.
- Blocs: `--left` (government blue) and `--right` (opposition red), only on bloc numbers.
- Type: Libre Franklin 400, 600, 700, 800 (self-hosted, Latin Extended-A for macrons). Headlines
  800 with negative tracking; numbers tabular. Mono only for code-like strings, nowhere on home.
- Widths: page `--wide` 1120 px, reading column `--text` 680 px. Gutters 16 px on phone.

## Page anatomy

1. Masthead: dark band, brand mark, route tabs (scroll horizontally on phone, never wrap to two
   rows).
2. Ribbon (home): the election phase today, a countdown, the one action ("How and where to vote").
3. Hero: kicker (one or three words), one question as the h1, the answer in one sentence, one
   big graphic, a two-line grey dek with the caveats, one footnote line.
4. Modules, in reader-question order: 3 px ink rule on top, h2 question, one dek sentence, one
   graphic, a foot row with the source line left and one "more" link right. `home.section()`
   renders this; use it on every page.
5. Footer: grey, two lines.

## Components (`pipeline/home_graphics.py`)

| Component | Function | Use |
|---|---|---|
| Seat hemicycle | `hemicycle(result)`, `seat_legend(result)` | one dot per seat, opposition left, government right, dashed radial at the majority, big bloc numbers under each end |
| Trend chart | `trend(averages, polls, election, wide=)` | all parties, polls as faint dots, 30-day average as thick lines (4 px over 15%), end labels with values, 5% line, shaded run-up to election day. Render `wide` and `narrow`; CSS shows one |
| Poll table | `poll_table(polls, average, names, count, reports=)` | heat-tinted cells (`--c`, `--a`), average row outlined first |
| Party cards | `party_cards(averages, result, leaders)` | leader photo ringed in party colour, share big, month change, bar, seats |
| Hex map | `hex_map(envs, cells, rows, held_for)`, `map_key` | electorates as hexes coloured by holder, three margin tones, each links to its page |
| Closest list | `closest_list(rows, held_for)` | name, holder, margin bar in party colour |
| Threshold bars | `threshold_bars(rows)` | 0 to 10% bars with the 5% line drawn through every bar |
| Market cards | `market_cards(entries)` | big percent, the question, a gauge |
| Timeline | `timeline(records, today)` | key dates, past greyed, today flagged |

New graphics go in this module, take data and return markup, and carry a hidden data table
(`hidden(table(...))`) so screen readers get the numbers.

## Rules that hold everywhere

- Absent means absent: no "not available" text; a module with no data returns '' and is dropped.
- Every number has a source reachable in one click (the module foot line, then Methods).
- Graphics are SVG with real `<text>`; never `preserveAspectRatio="none"`, never text scaled
  below 12 px on a 360 px phone (make a narrow variant instead).
- No horizontal page scroll at 360 px; wide tables scroll inside their own region with a sticky
  first column.
- Dark mode works: every colour is a token.

## How a design change is judged

Screenshots at 1280 and 390 of every changed page, in light mode, put beside the reference and
beside the previous version, looked at by the supervisor (not measured). Write down the three
weakest things on the page; fix or file them. See `REVIEW.md` pass 4 and "Design loop" in
`prompts/supervisor.md`.
