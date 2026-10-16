# NZ election: design brief

Status: draft 1, supervisor, 2026-10-17 NZ (day 2), written with the frontend-design skill for
Byron's steer in issue #15. Accepted when the design-system PR's two review rounds have passed
against it. Supersedes the Design section of `spec.md` where the two differ; `spec.md` rules on
accessibility, colour-never-alone and no-CDN stand.

## Subject, audience, job

The subject is the 2026 New Zealand general election under MMP: 120 seats, a 5 percent threshold,
71 electorates, two ticks on one ballot. The audience, in order: a voter on a phone in the two
weeks before 7 November who wants to know who is ahead and what that means in seats; a journalist
who needs a number they can cite with its source; a developer who wants the data and the night
client. The site's job is to answer "who is winning, by how much, and where did this come from" in
five seconds, and then let the reader go one level deeper without leaving the page.

## Direction: the ballot and the results board

Two things in this election's world are visually its own. The ballot paper: white, black rules,
two columns, a tick in a box. The results board on election night: a seat count that moves. The
design borrows the first for its structure and the second for its one bold element.

- The structure is a ledger. Black rules on white, left-aligned, two-column where the content is a
  pair (party vote and electorate vote; 2023 and 2026; counted and remaining). Rules carry meaning:
  a rule separates rows of the same kind, a double rule separates the answer from its evidence.
- The one bold element is the seat strip. It is the largest thing on the home page and the only
  place with large type and fills. Everything else is quiet, so the strip reads as the answer.
- The interaction cue is the tick. Links and controls gain an orange tick mark on hover and focus,
  the Commission's campaign colour used sparingly. No other orange.
- Nothing is a card. Content is not chopped into equal rounded boxes with shadows; grouping is done
  by rules and spacing. Border radius is zero everywhere except the focus ring.

What this is not: a dashboard of tiles, a cream broadsheet, a dark page with a neon accent, a
news site. The site is independent of the Electoral Commission and never imitates its logo or
its orange figure.

## Tokens

Colour, light mode (default):

| Token | Value | Use |
|---|---|---|
| paper | #FFFFFF | page ground |
| ink | #000000 | text, rules, strip outlines |
| grey | #5A5A5A | attribution, table headers, secondary text (7.0:1 on paper) |
| rule | #C8C8C8 | hairline rules inside tables (3.0:1 boundary on paper) |
| surface | #F0F2F4 | state bands, code, download rows on hover |
| tick | #F58220 | hover and focus tick mark only; never a fill behind text |
| focus | #005EA8 | 3 px focus outline with a 3 px paper gap |

Colour, night mode (election night view, M3; also honoured by `prefers-color-scheme` site-wide):

| Token | Value | Use |
|---|---|---|
| paper | #0F1A2B | page ground, a deep blue-black, not tinted black |
| ink | #F6F7F9 | text and rules |
| grey | #A9B2BF | secondary text (7.3:1 on night paper) |
| rule | #3A4658 | hairlines |
| surface | #182538 | bands |
| tick | #FFA347 | lifted orange for the live indicator and ticks |
| focus | #7CC4FF | focus outline, with a 3 px night-paper gap |

Party colours are data colours, not interface colours. They come from `config/party-colours.json`
with the evidence recorded there, are used only as fills in charts and the strip, and are always
paired with the party name and the number. Text never sits on a party fill; labels sit in ink on
paper beside or below the fill (ACT yellow and the two reds make this a rule, not a preference).
In night mode each fill gets a 1 px ink outline so adjacent dark fills (NZ First black, National
blue) stay separable. Every pairing in use is listed and its contrast checked by a test.

Type:

- Display: Bricolage Grotesque (OFL), self-hosted, one variable file subset to Latin plus Latin
  Extended-A (the macron set ā ē ī ō ū and capitals), used for the page title, the home sentence,
  the strip's seat numbers and the night count. Its wide optical cut at large sizes gives the
  numbers a board-like weight no system face has. Budget: one woff2 under 45 KB.
- Text: the system sans stack ("Helvetica Neue", Arial, system-ui, sans-serif) for everything else.
  Every face in the stack has macron glyphs and tabular figures; `font-variant-numeric:
  tabular-nums` on all tables and counts.
- Fallback rule: if the subset check (below) finds a missing macron glyph or no tabular figures in
  Bricolage, display falls back to Public Sans (OFL, both present) and this brief records the swap.
- Scale: 14 attribution, 16 body, 20 section, 28 page title, 44 home sentence on desktop and 32 on
  phone, 56 strip numbers on desktop and 40 on phone. Line height 1.5 for prose, 1.1 for display.
  Prose measure under 70 characters. Sentence case everywhere; no tracked caps labels; no labels
  above content that the content already states.
- Macron check: the design-system PR runs `uv run --with fonttools python -c` over the subset to
  assert glyphs for U+0100 to U+016B that NZ names use (Ā ā Ē ē Ī ī Ō ō Ū ū) and the `tnum`
  feature, and renders the 71 electorate names at 390 px in a screenshot that the review reads.

Layout:

- One column, max width 1120 px, left aligned, 16 px gutters on phone and 24 px on desktop. No
  centred text.
- Home at 390 px, top to bottom, inside the first viewport: the site name as one line; the home
  sentence; the seat strip with the majority marker; the provenance line. The threshold watch and
  the poll trend follow below the fold. At 1280 px the same order with the strip 160 px tall.

```
390 px                               1280 px
+------------------------------+     +------------------------------------------------+
| The open election desk  menu |     | The open election desk        polls electorates |
| National-led bloc 63 seats,  |     |                                                  |
| Labour-led 57, on polls to   |     | National-led bloc 63 seats, Labour-led 57,       |
| 14 October.                  |     | on polls to 14 October.                          |
| |NAT 44|LAB 34|GRN 13|ACT 9..|     | |  NAT 44  |  LAB 34  | GRN 13 | ACT 9 | NZF 8 | |
|   61 to govern  ^            |     |                      61 to govern ^              |
| From 9 polls, Wikipedia      |     | From 9 polls, Wikipedia revision 138052, allocated |
| revision 138052, allocated   |     | by this site. Downloads.                          |
| by this site. Downloads.     |     | ================================================ |
| ============================ |     | Threshold watch      |  Poll trend               |
| Threshold watch              |     +------------------------------------------------+
```

## Chart grammar

Every chart has a table equivalent reachable without hovering, a caption that says what it is,
and a provenance line that says where it came from. Charts are static SVG from the build except
the coalition explorer, which is the allowlisted module from increment 4.

- Seat strip (exists): proportional segments, counts inside segments that fit, leader lines to a
  label lane for small ones, majority marker at 61 with "61 to govern", overhang double-ruled.
- Poll trend: one line per party in its fill, pollster observations as small ink-outlined dots in
  the party fill, the average line heavier; the 5 percent rule drawn as a dashed ink line; x axis
  dates in NZ format "14 Oct"; the latest value labelled at the line end in ink, not in a legend.
  No shaded confidence bands (the method has none to justify).
- Threshold gauge: a horizontal 0 to 7 percent scale with the 5 percent rule as a vertical ink
  line, each party under 7 as a dot with its name and value to the right; an electorate-seat
  assumption shown as text, "qualifies with Epsom" beside the dot, never as a colour change.
- Map (exists): 71 outlines, selected electorate filled with the leading party's colour and named
  in ink beside the map; the Māori layer a separate map with the same grammar, never overlaid.
- Night waterfall (M3): one row per party, votes counted flowing left to right into seats, the
  remaining share of votes shown as an empty ruled box; percent counted as the page's live number
  in display type; time stamps in NZ time.

## Provenance chip

Every number that a reader could cite carries the same small line, in grey at 14 px, after the
number or under the chart: the source name, the date in NZ time, and a link to the download row
that produced it. Form: "From Electoral Commission, 2023 final results, captured 16 Oct" with the
whole phrase as one link. The chip never abbreviates a source to an acronym the reader has not
seen spelt out on that page. Hover and focus add the orange tick before the phrase. The downloads
page is the chip's destination and carries hash, size, observation range and the run that produced
it, as spec line 259 already requires.

## States

- Loading: the site is static, so no spinners. The explorer's recompute shows the changed numbers
  with no transition.
- Empty (no data yet): a surface band at the top of main: "No data yet. The first hourly refresh
  publishes it; this page then shows polls to that hour." with the refresh workflow linked.
- Stale: when the newest capture is older than its family's refresh interval times three, a
  surface band under the site name: "Last updated 14 Oct, 09:00. Refreshes run hourly; the last
  one failed." with the run linked. The numbers stay; the band says how old they are.
- Error (a family failed validation): the previous good bundle stays live; the band names the
  family and the attempt time. The page never shows a zero where it means missing.
- Missing (Port Waikato 2023, a seat with no candidate baseline): the row says "No 2023 contest"
  or "No candidate baseline for this electorate" in grey, never a dash, never zero.
- Unresolved (a poll naming an electorate the registry cannot map): listed under the table as
  "Not matched: Kāpiti (local poll)" so the reader sees what was excluded.

## Night mode

Election night is a dark room with a lit board. Night mode is the same ledger on night paper,
fills outlined, the live percent-counted number in display type, and the orange tick reserved for
the "live" indicator beside the last-updated time. It is the M3 view's default and the site-wide
response to `prefers-color-scheme: dark`. Motion: one orchestrated moment, the count ticking up
when a new feed arrives, 300 ms, disabled under `prefers-reduced-motion`. Nothing else moves.

## Identity assets

- Favicon: an SVG of a tick in a ruled box, ink on paper, 32 px legible; PNG fallbacks 180 and
  512 for the manifest.
- OG card per route: 1200 by 630, rendered by Playwright in the Pages workflow from `og.html`
  templates: the route's one sentence in display type, the strip or the electorate outline, the
  provenance line, the site name. One card per electorate so a shared electorate link shows that
  electorate.
- PWA manifest: name, short name, icons, `display: standalone`, `start_url` the night view in M3,
  theme colour night paper. Service worker: none (no offline promise; the data is live).

## Budgets and checks

- First view under 100 KB transferred before the map: HTML, CSS, the display font subset and the
  strip SVG. The 284 KB map SVG stays lazy, loaded below the fold or on the electorates page.
- CSS under 12 KB; one file; custom properties for the tokens above; no utility framework.
- Accessibility: axe-core vendored under `tests/` (never served) run by the screenshot harness on
  every route at 390 and 1280 with zero violations; keyboard order follows reading order; every
  control 44 px; focus visible; reduced motion honoured; headings form an outline.
- Contrast: a test enumerates every text and fill pairing from the token tables and the party
  colours file and asserts 4.5:1 for text, 3:1 for boundaries.

## Microcopy

Plain English, sentence case, active verbs. Numbers before names when the number is the point
("63 seats"), names before numbers in lists. "From" introduces a source. Dates in NZ format with
the month spelt short. Official electorate names with macrons as the Commission spells them, te reo
names unitalicised. The site calls itself by its name once per page, in the masthead. No
exclamation marks, no "simply", no "just".

## The five-second test

A first-time visitor on a 390 px phone, from a cold load of the home page, can say who is ahead
(the home sentence), by how much (the two bloc totals in the sentence and the strip against the
61 marker) and where the number came from (the provenance line) without scrolling. The review
states pass or fail from the 390 px screenshot alone and says which of the three answers is
missing when it fails.

## Design-system PR (before increment 7)

Scope: tokens into `styles.css`; display font subset and the macron check; the home sentence
generated from the current allocation with variants for no majority, a tie and no data; the
provenance chip component used by every existing number; states as above; the favicon, OG
template and manifest; the contrast and axe tests; the restyled M1 and M2 views (polls, strip,
threshold, electorates, directory, downloads, methods). No new data, no new routes except the OG
template. Definition of done: screenshots at 390 and 1280 of every route attached to the review
as images, the five-second test judged, two review-iterate rounds recorded in
`state/changes.yaml` as `design_rounds`.

## Open questions for the review rounds

1. Bricolage Grotesque against the subset check; Public Sans is the named fallback.
2. Whether the home sentence should name blocs ("National-led") or only parties: naming a bloc is
   an editorial claim about coalition intent. Draft rule: parties and totals from the explorer's
   default scenario, blocs only once a party has stated its preference on the record (source cited).
3. The night mode token set has not been seen on a screen yet; the M3 round may move the paper.
