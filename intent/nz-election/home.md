# NZ election: the feed home (intent and spec)

Change slug: `nz-election-home`. Part of the `nz-election` product change, M2 (v1 live before
advance voting opens on 26 October). Plan: `plan-home.md` beside this file, from a read-only
Codex plan job. Status: spec accepted by the supervisor 2026-10-17T09:10Z; Byron chose the
direction (issue #26).

## Intent

Byron, 2026-10-17 about 07:00Z (issue #26, relayed verbatim): "Yea i want the home page to use
this style: https://www.nbcnews.com/politics/2026-elections/midterms". It answers the 00:40Z
judgement call (reach-first home as a feed of chart cards) by reply. Earlier words that bind:
reach over usefulness, general users want graphics not downloads (issue #20); audiences and
tailored pages (issue #18); POC every new thing early and refine (issue #22).

Today the home route `/` is the polls page: the seat strip, the home sentence, the poll table,
the coalition explorer and the source notes. It answers one question well and shows nothing
else the site has: 71 electorate pages with candidates and 2023 results, the directory and map,
the social proof of concept, the night and campaign placeholders, the downloads and methods.
A first-time reader sees a table and leaves.

The change: the home becomes a feed in the shape of NBC's 2026 midterms hub, translated to MMP
and New Zealand data. Each module is one graphic with one sentence and one source line, and
links to the page that has the detail. The polls page moves to `/polls/` with its fragments
preserved. Electorate pages lead with candidates. `/night/` becomes results-first copy with the
countdown until results exist. Every route gets its own OG image (deferred from PR #21).

Success: a reader at 390 px understands within five seconds that this is the 2026 NZ election,
how many days remain, who leads the seat calculation, and where to look next; the home screenshot
reads as a feed of graphics, not a table; nothing published on it lacks a source line.

## The NBC shape and its translation

The operator fetched the NBC page at 07:05Z (issue #26). Its order and the home's answer:

| NBC module | Home module (route anchor) | Data already published |
|---|---|---|
| Sub-nav tabs and state list | Section tabs: Polls, Seats, Electorates, Night, Social, under the site header; a jump list at the end of the hero | routes |
| Hero: title, updated time, countdown, framing paragraph, jump links | Title "New Zealand votes on 7 November 2026"; "{N} days until election day" from the build time in NZ time; updated time; the home sentence as the framing line; jump links | status.json, seats.json |
| Battle for control: seat strip, stacked rating bar, majority marker, tally, legend | "Seats from current polls" (`#seats`): the existing 120-seat proportional strip with the "61 for a majority" marker, party seat rows, the 5 percent and electorate-seat threshold watch; legend as a details element | seats.json, averages.json |
| Latest polling: two stat cards | "Where the party vote stands" (`#polls`): the window average per party as large figures, two columns (the two largest parties), the rest in a row; fieldwork range and the source line; link "All polls" to `/polls/` | averages.json, polls.json |
| More polling coverage | Not built: no stories exist. The slot carries "How seats are calculated" and "Explore seat combinations" links | |
| Senate battlegrounds: wide race cards | "Electorates to watch" (`#electorates`): six wide cards, the closest 2023 margins on unchanged boundaries, each with the electorate name, the margin line, the top candidates by party, incumbent marker, "More" to the electorate page | baseline-2023.json, candidates.json, electorates.json |
| House battlegrounds: grid of small cards | "All 71 electorates" (`#directory`): the compact grid of every electorate (name, held-by party mark, boundary flag), linking to the page; one column at 390 px | electorates.json, baseline-2023.json |
| Governor section | Not built (no analogue) | |
| Live updates and story lists | "What people are posting" (`#social`): the social proof of concept's one chart with its sample size and date range, labelled as a proof of concept, link to `social/poc/`; empty state when no run has published | social family |
| How NBC projects races | "How this site calculates seats" (`#method`): three short paragraphs and the link to `/methods/`; the licence line | |

Markets (increment 7) take a module under `#polls` when `markets.json` exists; the home must
render without it. Headshots: none (licensing, issue #26); candidates carry a party mark.

## Numbered requirements

- H1. Route `/` renders the feed above in that order; `/polls/` renders today's polls page
  unchanged in content, and every fragment id that exists on today's home (`#seats`,
  `#polls`, `#explorer`, the source-note ids, any id a test or a shared link uses) resolves on
  `/polls/`; `/` keeps `#seats` and `#polls` pointing at its own modules. The plan lists the
  fragment inventory from the templates and tests before it moves anything.
- H2. Countdown: "{N} days until election day" computed from the build time in Pacific/Auckland
  against 2026-11-07; "Election day" on the day; after it, the hero line becomes "Results"
  copy per the night transition (H6). The number is rendered by the build, never by a script.
- H3. The seat module reuses the strip, rows and threshold watch of today's home as components
  (one template partial, one CSS block), so the home and `/polls/` cannot drift.
- H4. The poll module shows the window average per party to one decimal with tabular numerals,
  the fieldwork range sentence, the pollster count, the source line (Wikipedia CC BY-SA 4.0
  with revision link, as today). Nothing is interpolated; no trend arrows unless the average
  file already carries the previous window.
- H5. Electorates to watch: a stated, published selection rule. Default rule: the six smallest
  2023 winning margins among electorates whose 2025 boundary is unchanged per the
  correspondence file; electorates with changed boundaries are excluded from the ranking and
  the module says so in one sentence. No rating labels (Solid, Lean, Toss-up): no electorate
  polling base exists, and a rating from one old margin would read as a forecast. Each card:
  name with macrons, "Held by {party}, {N} votes in 2023 on the original boundaries",
  candidates as "{Name} ({Party})" for the parties with a published candidate, incumbent
  marker, "More" link. If `baseline-2023.json` or `candidates.json` is absent, the module
  renders "Not available" with the reason (the publish contract), never an empty card.
- H6. `/night/` becomes results-first copy: the countdown line, "Results appear here from 7 pm
  on 7 November", what the page will show (places counted, seat waterfall, party table), the
  publication freeze sentence (no publication between 00:00 and 19:00 NZDT on election day,
  Electoral Act s197), and a link to the official Electoral Commission results site. Still a
  placeholder in data terms; the structure is for M3.
- H7. Electorate pages: candidates first (already so in the template), then the summary line
  the home card uses, then the rest in today's order. Each page's `<title>` and OG description
  name the electorate and its held-by party.
- H8. Per-route OG image: `og.html` renders one 1200 by 630 image per route at build time with
  the route's headline figure (home: the seat strip; polls: the top two averages; electorate:
  the name and held-by line; others: the page title), written to
  `site/nz-election/og/<route>.png` by the screenshot harness on the host and referenced by
  `og:image` and `twitter:image` with absolute URLs. The harness image count grows by the
  route count; the plan says the exact number. The build never runs a browser.
- H9. Social module: reads the social family's published aggregate; shows the single chart the
  POC shows, its sample size and date range, the "Proof of concept" label, and the link. The
  s197 freeze logic lives in the social workflow, not here; the home renders whatever was last
  published with its date.
- H10. Navigation: the site header gains "Home"; "Polls and seats" points at `/polls/`. The
  section tabs under the header are in-page anchors on the home only. The phone menu stays.
- H11. Every module has one source note in the existing `source-note.html` shape and an
  `aria-describedby` from its figure to that note; the verifier's MISSING_SOURCE and
  SMALL_TARGET checks apply to the home.
- H12. Screenshots at 390 by 844 and 1280 by 800 of `/`, `/polls/`, `/night/` and one
  electorate page, plus the keyboard-focus state on a home card, are part of the definition of
  done; the fresh review judges them.

## Design

The design system from PR #21 (`design.md`: tokens, type stack, states, source notes, budgets)
stands. NBC's structure is adopted; its costume is not. Resolved against "Nothing is a card":

- A home module is a region separated by a single ink rule above it, its heading at the 20 px
  size in sentence case, its figure, its sentence, its source line. No border radius, no shadow,
  no filled background. The "race cards" in the electorate module are rows of the same ledger:
  a rule between rows, two columns at 800 px and up, one column below.
- The one bold element on the home stays the seat strip in the hero module. The poll module's
  large figures are the 40 px size in the strip's own type, not a second hero; party colour
  appears only as the party fill swatch beside the figure, never as text colour.
- The countdown is set in the same 40 px size as a number with its unit in body type beneath it;
  it sits beside the title at 1280 px and below it at 390 px.
- Section tabs are underlined ink links in a horizontal list that scrolls at 390 px; the current
  section is marked with the selection tick, not a colour.
- Copy is for a voter: "Seats from current polls", "Where the party vote stands", "Electorates to
  watch", "All 71 electorates", "What people are posting", "How this site calculates seats".
  No eyebrows, no all-caps labels, no icons.
- Motion: none on load. The only motion is the existing explorer response on `/polls/`.
- Night mode: the tokens already honour `prefers-color-scheme`; the modules inherit it.

Wireframe, 390 px, top to bottom: header; tabs; title; countdown; home sentence; jump list;
rule; seat strip with the 61 marker; party rows; threshold watch; rule; two large averages;
rest of parties in a row; fieldwork and source; rule; six electorate rows; rule; directory grid
one column; rule; social chart; rule; method paragraphs; footer. At 1280 px the hero puts the
countdown right of the title, the seat module keeps full width, the poll module is two columns,
the electorate rows are two columns, the directory grid is four columns.

Checked against the frontend-design skill: the hero opens with the most characteristic thing
(the seat strip, not a standalone number); one family of type; structure carries meaning
(rules separate modules, no decorative chrome); the memorable element is one thing; no load
motion; copy written for the reader.

## Constraints

- Static build, no runtime library, no fonts, no bundler; Python standard library; the build
  never fetches. Pages weight: the home under 200 KB of HTML and CSS before images.
- The route registry, verify.py checks, screenshot harness and tests move with the registered
  set (contracts move with the set, nothing weaker). Route count 78 grows by one (`/polls/`).
- `data/` is unchanged by this change; no new upstream, no new secret.
- Markets (increment 7) is a separate change; the home renders with or without `markets.json`.
- Candidate headshots: none. Raw posts, handles and keys: none anywhere.

## Verification

- `uv run --with pytest pytest -q product/nz_election` passes with the new tests the plan names
  (route inventory 79, fragment inventory on `/polls/`, countdown arithmetic at three fixed
  times, electorate selection rule with the boundary exclusion, OG image reference per route).
- `uv run product/nz_election/pipeline/verify.py all` prints PASS for every check including
  the home.
- On the host: `uv run product/nz_election/tests/screenshots.py` passes with the route and image
  counts the plan states, and the supervisor looks at the home at both sizes.
- `bin/lint` ok.

## Out of scope

Ratings, forecasts, headshots, stories, a live-updates module, any new data family, the night
feed (M3), the campaign page (M3), analytics.
