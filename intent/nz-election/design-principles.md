# NZ election: design principles (issue #34)

Byron, Telegram 2026-10-18 21:58Z (issue #34): "There's a lot of bad design choices made in there.
Use the reference site to influence the design starting by creating design principles based on the
site and then implementing. Some example of what is bad. Overall color / layout. Too many
collapsibles, too many references flooding the main page etc"

Reference: the 538 2024 forecast,
https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/

Written by the supervisor 2026-10-18T22:45Z. These rules bind every page and override `design.md`
and `look-538.md` where they conflict; `look-538.md` tokens and type stay unless a rule below
changes them. Each rule names the 538 element it comes from and how it applies here.

## Baseline (live home, 2026-10-18 22:20Z, operator measure)

9 `<details>`, 314 links, 135 occurrences of "source", 70 KB HTML, 10 question headings.

## The rules

1. **One answer, said once, big.** 538: the page opens with one sentence ("Harris wins 50 times
   out of 100") and one chart, nothing beside it. Here: the hero is the seat answer only, the
   headline question, two bloc lines ("Government 67 seats", "Opposition 58 seats", "61 needed"),
   one seat bar ordered by bloc, and one line under it: the date of the average and a link to how
   it is made. No other module, notice or link shares the hero's row.

2. **Two colours carry all the meaning; everything else is grey.** 538: blue and red appear only
   on data about the two candidates; type is black, chrome and secondary data are grey, ground is
   white. Here: Government blue and Opposition coral (NZ convention: National blue, Labour red;
   the #33 swap is fixed in PR #35) are used only on bloc-level numbers and marks. Party-level
   charts use party colours only where the party is the subject (polls chart, threshold watch).
   No coloured backgrounds, badges, buttons or decorative rules. The notice yellow appears at most
   once per page, and only for a state the reader must know (stale data, proof of concept, freeze).

3. **A single column of modules in order of importance, not a grid of equals.** 538: below the
   hero, full-width sections in a fixed reading order, each a question heading, a one-line dek and
   one graphic. Here: home is hero, then at most six modules: latest polls, poll trend, closest
   electorates, threshold watch, prediction markets, election night. Anything else (social POC,
   coalition statements, timeline detail) is one link in a closing "More" list, not a module.
   Each module: question h2, one dek sentence, one graphic or table, one "See all" link.

4. **Show, do not disclose.** 538: no disclosure widgets on the forecast page; the chart is open,
   the method is a separate page. Here: zero `<details>` on the home page. A caveat that changes
   how a number is read is one sentence in the dek; everything else moves to the methods page.
   Other routes may use `<details>` only for long tables (all polls, all electorates).

5. **Sources at the foot, not on every figure.** 538: one small grey line under each graphic
   ("Sources: polls, our model"); the full list is on the methodology page. Here: one footnote
   line per module, grey, small, naming the source and the update time, linking to that module's
   anchor on a sources page (`/sources/` or `methods/`, whichever exists). The no-unsourced-figure
   rule still holds: every figure's full provenance (poll list, revision, fetch time, derivations
   such as Others-as-remainder) is reachable in one click and lives on the sources page. Nothing is
   deleted; it moves. Inline "source" chips on individual figures are removed from home.

6. **Quiet type, one scale, no chrome.** 538: one sans family, bold question headings, grey deks,
   no eyebrows, no all-caps labels, no icons in headings. Here: Libre Franklin as in
   `look-538.md`; mono only for timestamps and table figures; no tracked caps, no middle-dot meta
   strings, no arrows appended to links, no card borders, shadows or radius.

7. **Whitespace is the divider.** 538: sections separated by space and one hairline, not boxes.
   Here: 64 px between modules on desktop, 40 px on phone, one hairline above each module heading,
   nothing else.

8. **Navigation is small and stays out of the way.** 538: race tabs in the masthead, nothing
   sticky that covers content. Here: the masthead route tabs stay; the section nav is one row
   under the masthead on desktop and is dropped on phone if it covers content (no fixed bottom bar
   over the chart).

## Checks the restyle must pass (on top of `design.md` budgets)

Home page, measured the same way as the baseline:

| Measure | Baseline | Target |
|---|---|---|
| `<details>` | 9 | 0 |
| links | 314 | under 60 |
| "source" occurrences (case-insensitive, rendered text) | 135 | under 12 (one per module plus nav) |
| HTML bytes | 70 KB | under 35 KB |
| modules (h2 questions) | 10 | at most 6, plus the "More" list |
| bloc colours used outside bloc data | not measured | 0 |

The sources page holds every provenance item removed from home; a test asserts that each figure
id on home has an entry there (move, not delete). Screenshots of home and the sources page at 360,
390 and 1280, before and after, are part of done and go in the PR body with this doc's link.

## Not this

538's logo, mascot, illustrations, Franklin Gothic, copied copy; probabilities without a model
(that waits for the L-b simulation POC).
