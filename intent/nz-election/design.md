# NZ election: design brief

Status: draft 2, supervisor, 2026-10-17 NZ (day 3), written with the frontend-design skill for
Byron's steer in issue #15 and revised against the read-only critique review-design-nz-election
(nine Important, two nits; every finding and its resolution is in the "Critique round 1" section
at the end). Accepted when the design-system PR's two review rounds have passed against it.
Supersedes the Design section of `spec.md` where the two differ; `spec.md` rules on accessibility,
colour-never-alone, provenance (line 244), staleness (line 257) and no-CDN stand and win on
conflict.

## Subject, audience, job

The subject is the 2026 New Zealand general election under MMP: 120 seats, a 5 percent threshold,
71 electorates, two ticks on one ballot. The audience, in order: a voter on a phone in the two
weeks before 7 November who wants to know who is ahead and what that means in seats; a journalist
who needs a number they can cite with its source; a developer who wants the data and the night
client. The site's job is to answer "who is ahead, by how much, and where did this come from" in
five seconds, and then let the reader go one level deeper without leaving the page.

## Direction: the ballot and the results board

Two things in this election's world are visually its own. The ballot paper: white, black rules,
two columns, a tick in a box. The results board on election night: a seat count that moves. The
design borrows the first for its structure and the second for its one bold element.

- The structure is a ledger. Black rules on white, left-aligned, two-column where the content is a
  pair (party vote and electorate vote; 2023 and 2026; counted and remaining). Rules carry meaning:
  a rule separates rows of the same kind, a double rule separates the answer from its evidence.
  Because rules carry meaning they meet the 3:1 boundary ratio; no decorative hairlines.
- The one bold element is the seat strip. It is the largest thing on the home page and the only
  place with large type and fills. Everything else is quiet, so the strip reads as the answer.
- The tick marks selection, not navigation. A ticked box (ink outline, burnt-orange tick) shows
  the selected electorate in the directory, the selected layer, the parties included in an
  explorer scenario, the row a shared link points at. Links are underlined ink; hover thickens the
  underline; focus is the blue ring. Orange appears nowhere else in light mode. At night the
  lifted orange belongs to the "live" indicator alone and selection ticks are ink.
- Nothing is a card. Content is not chopped into equal rounded boxes with shadows; grouping is done
  by rules and spacing. Border radius is zero everywhere except the focus ring.

What this is not: a dashboard of tiles, a cream broadsheet, a dark page with a neon accent, a
news site. The ledger is a structure, not a costume: the subject-specific decisions are the
proportional seat composition, the two-tick selection grammar and the pairing of every number
with its source. The site is independent of the Electoral Commission and never imitates its logo
or its orange figure.

## Tokens

Colour, light mode (default). Ratios are WCAG relative luminance against paper, to be asserted by
the contrast test, not trusted from this table:

| Token | Value | Use | Ratio on paper |
|---|---|---|---:|
| paper | #FFFFFF | page ground | |
| ink | #000000 | text, rules that separate answer from evidence, fill outlines | 21:1 |
| grey | #5A5A5A | attribution, table headers, secondary text | 6.9:1 |
| rule | #8A8A8A | hairline rules inside tables (meaningful boundary) | 3.1:1 |
| surface | #F0F2F4 | state bands, code, download rows on hover | |
| tick | #B4500A | the selection tick inside its ink box; never a fill behind text, never a link colour | 5.1:1 |
| focus | #005EA8 | 3 px focus outline with a 3 px paper gap | 6.6:1 |

Colour, night mode (election night view, M3; also honoured by `prefers-color-scheme` site-wide):

| Token | Value | Use | Ratio on night paper |
|---|---|---|---:|
| paper | #0F1A2B | page ground, a deep blue-black, not tinted black | |
| ink | #F6F7F9 | text, rules, fill outlines, selection ticks | |
| grey | #A9B2BF | secondary text | 8.2:1 |
| rule | #60697A | hairlines (meaningful boundary) | 3.2:1 |
| surface | #182538 | bands | |
| live | #FFA347 | the live indicator beside the last-updated time, nothing else | 8.8:1 |
| focus | #7CC4FF | focus outline, with a 3 px night-paper gap | 9.3:1 |

Party colours are data colours, not interface colours. They come from `config/party-colours.json`
with the evidence recorded there (sampled fills: National blue, Labour red, Green green, ACT pink,
NZ First navy, Te Pāti Māori black-red, Opportunity teal), are used only as fills in charts and
the strip, and are always paired with the party name and the number. Text never sits on a party
fill; labels sit in ink on paper beside or below the fill. Every fill carries a 1 px ink outline
in both modes (Opportunity on white, Green and NZ First on night paper fall under 3:1 without it;
one rule for all is simpler than a per-mode exception list). Every pairing in use is enumerated
and checked by a test: text on paper and surface at 4.5:1, rules and fill outlines at 3:1, in both
modes.

Type:

- One family for this iteration: the system sans stack ("Helvetica Neue", Arial, system-ui,
  sans-serif). Every face in the stack has macron glyphs and tabular figures;
  `font-variant-numeric: tabular-nums` on all tables and counts. Display sizes get the board-like
  weight from size, weight 700 and tight leading, not from a downloaded face.
- Display font deferred: Bricolage Grotesque (OFL, self-hosted, Latin plus Latin Extended-A
  subset, one woff2 under 45 KB, Public Sans as the named fallback) is the candidate for the page
  title, home sentence, strip numbers and night count. It is not in the design-system PR. A later
  comparison round renders the home page both ways from real data, with fallback wrapping and
  font-loading behaviour, and the brief records the decision. Until then the font budget below is
  reserved, not spent.
- Scale: 14 attribution, 16 body, 20 section, 28 page title, 32 home sentence on desktop and 26 on
  phone, 48 strip numbers on desktop and 32 on phone. Line height 1.5 for prose, 1.15 for display.
  Prose measure under 70 characters. Sentence case everywhere; no tracked caps labels; no labels
  above content that the content already states.
- Macron check: the screenshot harness renders the 71 electorate names at 390 px and the review
  reads the image; the font check with fonttools moves to the comparison round.

Layout:

- One column, max width 1120 px, left aligned, 16 px gutters on phone and 24 px on desktop. No
  centred text.
- First viewport budget at 390 by 844 (and 360 by 780, which REVIEW.md requires): masthead one
  line with a collapsed menu (a `details` element listing the routes, no script) 48 px; home
  sentence two lines at 26/30 plus the dates line 14/21, about 90 px; the strip 72 px; the
  label row under the strip one or two lines of 14/21, up to 42 px; the majority marker label
  21 px; the provenance note three lines of 14/21, 63 px; spacing 16 px between blocks, about 100
  px. Total about 440 px, inside 780. The threshold watch, the poll trend and the full seat table
  follow below. At 1280 px the same order with the strip 120 px tall and the labels in one row.
  The screenshot harness asserts that the provenance note's bottom edge is above 780 px at 360
  and 390 with the fixture data, and the review judges the five-second test from the image.

```
390 px                               1280 px
+------------------------------+     +------------------------------------------------+
| The open election desk  Menu |     | The open election desk   Polls  Electorates ... |
| National leads with 44       |     |                                                  |
| calculated seats; no party   |     | National leads with 44 calculated seats; no      |
| reaches the assumed majority |     | party reaches the assumed majority of 61.        |
| of 61.                       |     | Polls 2 Sep to 14 Oct. How seats are calculated. |
| Polls 2 Sep to 14 Oct.       |     |                                                  |
| How seats are calculated.    |     | |###########|##########|####|###|##|##|          |
| |#########|########|###|##|#|.|    |  NAT 44  LAB 34  GRN 13  TPM 12  ACT 9  NZF 8    |
| NAT 44 LAB 34 GRN 13 TPM 12  |     |                        ^ 61 for a majority       |
| ACT 9 NZF 8                  |     | From 9 polls listed by Wikipedia contributors    |
|          ^ 61 for a majority |     | (CC BY-SA 4.0), revision 1380524613, retrieved   |
| From 9 polls listed by       |     | 17 Oct 2:17 pm NZDT. Seats calculated by this    |
| Wikipedia contributors (CC   |     | site: method, inputs, data run.                  |
| BY-SA 4.0), revision 138052, |     | ================================================ |
| retrieved 17 Oct 2:17 pm.    |     | Threshold watch      |  Poll trend               |
| Seats by this site: method.  |     +------------------------------------------------+
| ============================ |
| Threshold watch              |
```

## The home sentence

Generated by the build from the explorer's default scenario (`selected=[]`, default electorate
assumptions), never from a bloc or coalition the site has inferred. M is `assumed_majority` from
the allocation, including overhang, so it reads 61 only when the House is 120. Four exact forms:

- Majority: "{Party}: {N} calculated seats, reaching the assumed majority of {M}."
- No majority: "{Party} leads with {N} calculated seats; no party reaches the assumed majority of
  {M}."
- Tie for the lead: "{Party A} and {Party B} are level on {N} calculated seats; no party reaches
  the assumed majority of {M}." (A three-way tie lists all three.)
- No data: "No seat estimate available yet." followed by the link "Read how seats are calculated."

Directly beneath, one line in grey: the fieldwork range of the polls in the average ("Polls 2 Sep
to 14 Oct") and the link "How seats are calculated" to the methods page. The majority marker on
the strip is labelled "{M} for a majority", never "to govern": a majority of seats is a
calculation; forming a government is not.

## Chart grammar

Every chart has a table equivalent reachable without hovering, a caption that says what it is,
and a source note that says where it came from. Charts are static SVG from the build except the
coalition explorer, which is the allowlisted module from increment 4.

- Seat strip (exists, to be restyled): proportional segments with 1 px ink outlines, overhang
  double-ruled, the majority marker a vertical ink line through the strip with "{M} for a
  majority" beneath. One label treatment: no text inside segments, no white patches on fills.
  Labels are "{ABBR} {N}" in ink on paper in a row under the strip, each starting at its segment's
  left edge where the segment is wide enough for the label, otherwise flowing on after the
  previous label with a short leader line to the segment. On phone the row may wrap to a second
  line; never more. Height budget: strip 72 px plus at most 42 px of labels at 390. The existing
  four-lane layout (about 408 px at 390) and the in-segment white label patches are removed; this
  is the resolution of `spec.md` line 274's "text outside coloured segments".
- Poll trend: one line per party in its fill with an ink outline on the latest point, pollster
  observations as small ink-outlined dots in the party fill, the average line heavier; the 5
  percent rule drawn as a dashed ink line; x axis dates in NZ format "14 Oct"; the latest value
  labelled at the line end in ink, not in a legend. No shaded confidence bands (the method has
  none to justify).
- Threshold gauge: a horizontal 0 to 7 percent scale with the 5 percent rule as a vertical ink
  line, each party under 7 as a dot with its name and value to the right; an electorate-seat
  assumption shown as text, "qualifies with Epsom" beside the dot, never as a colour change.
- Map (exists): 71 outlines in rule grey, the selected electorate drawn with a 2 px ink outline
  and surface fill and named in ink beside the map; the Māori layer a separate map with the same
  grammar, never overlaid. No party fills in M2: the site holds 2023 results on 2023 boundaries
  and has no comparable "leading party" measure for the 2025 electorates. A party fill may be
  introduced only with a named measure (candidate vote or party vote), a stated year, a matching
  boundary basis and a dated source, all printed beside the map.
- Night waterfall (M3): one row per party, votes counted flowing left to right into seats, the
  page's live number in display type is "{X}% of voting places reported" because that is what the
  feed measures. No remaining-votes box and no "percent counted" unless the source supplies a
  defensible denominator, in which case the note names it. Replay, illustrative replay and
  live-unavailable each carry their own visible label above the count before the orange live
  indicator is ever drawn; the live indicator appears only for a live feed with a successful
  response inside 90 seconds.

## Source notes

The provenance element is the `source-note` component that `spec.md` line 244 specifies: a grey
14 px paragraph with the original source as a link in the source's own words (not an acronym the
page has not spelt out), the licence, the fieldwork or result date, the retrieval time in
Pacific/Auckland with NZST or NZDT, and, for a calculation, links to its method, its inputs and
the data run. The downloads page is one more destination, not the only source link. Where the
notes sit:

- Tables: one note beside the caption for the whole table; row-level references only where a
  row's source or date differs from the table's, as a superscript letter pointing at a second
  note below the table.
- Strips and charts: one note directly under the graphic, before the equivalent table.
- A single number in prose: one note adjacent to it.
- Maps: boundary attribution under the map, plus a separate note with the source and date of the
  selected result.

Every numeric group is linked programmatically to its note (`aria-describedby` from the table,
the SVG or the number to the note's id). Dates in a note are typed: fieldwork ended, results
final, retrieved. The note never shows a retrieval time where a fieldwork date belongs.

## States

Reader-facing words only: "polls", "previous data", "update details", "2023 candidate results".
Technical identifiers (family, bundle, refresh workflow, run id) appear inside the linked update
details, not in the band. Every state below has a treatment and a fixture in the screenshot
harness.

- Loading: the site is static, so no spinners. The explorer's recompute shows the changed numbers
  with no transition.
- No data yet (nothing has ever been published for this page): a surface band at the top of
  main: "No data yet. Polls are checked hourly." with "Update details" linked. The home sentence
  is its no-data form.
- Overdue (newest successful update older than its interval: 3 hours for polls, 36 hours for
  daily data, 90 seconds for live): a surface band under the masthead: "Update overdue. Last
  checked {time NZ}. Showing polls to {time NZ}." with "Update details" linked. Age alone does not
  claim a failure.
- Update failed, previous data shown (a recorded failed attempt with an earlier success): "The
  {time NZ} update failed; showing previous data from {time NZ}." with "Update details" linked.
  The numbers stay and are labelled with their own time; nothing is re-dated.
- Unavailable (a recorded failed attempt and no previous success): the no-data band with "The
  {time NZ} update failed." added. The page never shows a zero where it means missing.
- Polls present, seats unavailable (the allocation could not run or is withheld as stale): the
  home sentence takes its no-data form while the poll table stays; the strip is replaced by one
  line, "Seat estimate unavailable. Polls to {date} are below." A stale allocation is never shown
  as current.
- Explorer inputs incomplete, shared scenario invalid or from an older data version, electorate
  count invalid: the explorer keeps the last valid result on screen and says in a surface line
  under the controls what was rejected and that the last valid scenario is shown (the copy that
  `coalitions.mjs` already uses, restyled, not rewritten).
- Unresolved allocation tie: the affected seats are listed under the strip as "Tie for the last
  seat between {A} and {B}; shown unassigned." in grey.
- Candidate-source conflict, boundary comparison unresolved: the electorate page row says which
  sources disagree or why 2023 cannot be compared, using the wording `electorate_pages.py`
  already renders.
- Missing (Port Waikato 2023, a seat with no candidate baseline): the row says "No 2023 contest"
  or "No 2023 candidate results for this electorate" in grey, never a dash, never zero.
- Unresolved (a poll naming an electorate the registry cannot map): listed under the table as
  "Not matched: Kāpiti (local poll)" so the reader sees what was excluded.
- Offline verification (the build ran with no network, fixtures only): the downloads page labels
  the data run "fixture run"; nothing on the home page changes.

## Night mode

Election night is a dark room with a lit board. Night mode is the same ledger on night paper,
fills outlined, the live count in display type, and the lifted orange reserved for the "live"
indicator beside the last-updated time. It is the M3 view's default and the site-wide response
to `prefers-color-scheme: dark`. Motion: one orchestrated moment, the count ticking up when a
new feed arrives, 300 ms, disabled under `prefers-reduced-motion`. Nothing else moves. The night
tokens have not been seen on a screen; the design-system PR ships them behind the media query
and includes one night screenshot of the home page so the M3 round starts from evidence.

## Identity assets

- Favicon: an SVG of a tick in a ruled box, ink on paper, 32 px legible; PNG fallbacks 180 and
  512 for the manifest.
- OG card per route: 1200 by 630, rendered by Playwright in the Pages workflow from an `og.html`
  template: the route's one sentence in display type, the strip or the electorate outline, the
  source note, the site name. One card per electorate so a shared electorate link shows that
  electorate.
- PWA manifest: name, short name, icons, `display: standalone`, `start_url` the night view in M3,
  theme colour night paper. Service worker: none (no offline promise; the data is live).

## Budgets and checks

- First view under 100 KB transferred (decimal) before the map: HTML, CSS and the strip SVG, plus
  the explorer modules and their startup JSON on the home page if the explorer stays there. The
  test measures the built home page with its linked assets, gzipped sizes where Pages compresses
  (HTML, CSS, SVG, JS, JSON), from a real build with the fixture bundle; the display font's 45 KB
  is reserved inside the 100 KB and stays unspent this iteration. The 284 KB map SVG stays lazy,
  loaded below the fold or on the electorates page.
- CSS under 12 KB raw; one file; custom properties for the tokens above; no utility framework.
- Accessibility: axe-core vendored under `tests/` (never served) run by the screenshot harness on
  every route at 390 and 1280 with zero violations; keyboard order follows reading order; every
  control 44 px; focus visible; reduced motion honoured; headings form an outline.
- Contrast: a test enumerates every text and fill pairing from the token tables and the party
  colours file, in both modes, and asserts 4.5:1 for text, 3:1 for rules and fill outlines.
- Viewport: the harness asserts the first-viewport budget above at 360 and 390.

## Microcopy

Plain English, sentence case, active verbs. Numbers before names when the number is the point
("44 calculated seats"), names before numbers in lists. "From" introduces a source. Dates in NZ
format with the month spelt short. Official electorate names with macrons as the Commission
spells them, te reo names unitalicised. The site calls itself by its name once per page, in the
masthead. No exclamation marks, no "simply", no "just". "Calculated seats" and "assumed
majority", never "projected", "predicted" or "to govern".

## The five-second test

A first-time visitor on a 390 px phone, from a cold load of the home page, can say who is ahead
(the home sentence), by how much (the leading count against the majority M in the sentence and
the strip against the marker) and where the number came from (the source note) without
scrolling. The review states pass or fail from the 390 px screenshot alone and says which of the
three answers is missing when it fails.

## Design-system PR (before increment 7)

Scope: tokens into `styles.css` for both modes; the home sentence generated from the current
allocation in its four forms; the strip restyled to the one label treatment; the collapsed phone
menu; the `source-note` placements and `aria-describedby` links on every numeric group; the
states above with fixtures; the favicon, OG template and manifest; the contrast, axe, viewport
and first-view budget tests; the restyled M1 and M2 views (home and polls, strip, threshold,
electorates and map, directory, 71 electorate pages, downloads, methods); one night screenshot of
the home page. No new data, no new routes except the OG template, no display font. Definition of
done: screenshots at 360, 390 and 1280 of every route type attached to the review as images, the
five-second test judged, two review-iterate rounds recorded in `state/changes.yaml` as
`design_rounds`.

## Open questions for the review rounds

1. Display font: decided by the comparison round after the restyle, not before.
2. Whether the home sentence should ever name blocs: not in M2. Blocs appear only inside the
   explorer when the reader selects them, or once a party has stated its preference on the
   record (source cited), as a labelled scenario, never as the default sentence.
3. The night token set has not been seen on a screen; the M3 round may move the paper.
4. Whether the explorer stays on the home page or moves to its own route once the first-view
   budget test measures it with its JSON.

## Critique round 1 (review-design-nz-election, read-only, 169 s)

| Finding | Resolution in draft 2 |
|---|---|
| 1 First viewport about 919 to 974 px at 390 | Shorter sentence, strip 72 px, one label row, collapsed menu, source note before the table, viewport asserted at 360 and 390 |
| 2 Rule 1.67:1, night rule 1.83:1, tick 2.59:1, Opportunity, Green, NZ First fills | Rule #8A8A8A, night rule #60697A, tick #B4500A inside an ink box, 1 px ink outline on every fill in both modes, grey stated as 6.9:1 |
| 3 Headline invents coalitions, "61 to govern" | Four exact sentence forms from the default scenario, M from assumed_majority, marker "{M} for a majority" |
| 4 Chip too repetitive and too thin | Source notes per group with placements, row references by exception, spec 244 fields, typed dates |
| 5 Stale timing and copy | 3 h, 36 h, 90 s from spec 257; overdue, failed-with-previous and unavailable distinguished |
| 6 State inventory incomplete and technical | Twelve states with reader-facing words and fixtures |
| 7 Strip labels contradict the no-text-on-fills rule | One external label treatment; patches and lanes removed; ACT pink, NZ First navy |
| 8 Map leading party undefined | Neutral selected outline in M2; party fills gated on measure, year, boundary, source |
| 9 Waterfall implies a known total | "{X}% of voting places reported"; no remaining box without a denominator; replay labels |
| 10 Nit: font not justified | System stack this iteration; comparison round later |
| 11 Nit: ledger as costume, orange ticks on links | Ticks mark selection only, links underlined; direction names the subject-specific decisions |
