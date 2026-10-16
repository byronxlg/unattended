# Intent: NZ Election 2026

Originator: Byron (issue #7, 2026-10-16), written up and accepted by the supervisor (Claude)
2026-10-17 NZ (day 2). Change kind: product. Byron's words: "I want something with a ui and a
web app. The nz elections are coming up maybe something to do with that. What is interesting
is pulling a ton of information and displaying it."

## Problem

New Zealand votes on 7 November 2026 (advance voting from 26 October, enrolment closes
25 October, official results 27 November). The information a voter or a politics watcher wants
is scattered: polls on Wikipedia and pollster sites, seat maths in the Electoral Act, candidates
in an Electoral Commission spreadsheet and a PDF, boundaries in a Stats NZ ArcGIS service (new
for 2025, so 2023 results do not line up), prediction markets on Polymarket, and on the night an
XML feed nobody outside the media has built an open client for. Every existing dashboard
(Herald, Stuff/The Post, RNZ, Newsroom, The Progress Report) is closed: no data download, no
published method, no source link per number. `intent/research/nz-election-data-sources.md`
is the inventory; read it before the spec.

## Proposed outcome

One static web app, mobile first, that pulls these sources together and shows them with a
source and timestamp on every number. Four views, shipped in this order:

1. **Polls and seats.** Every published 2026 poll (parsed from the Wikipedia table, CC BY-SA),
   a trend average, the s191 to s193 Sainte-Lague allocation to seats, a threshold watch for
   the parties near 5 percent, and a coalition explorer. Polymarket prices alongside the polls.
2. **71 electorates.** A map on the 2025 boundaries (Stats NZ, CC BY) and a page per electorate:
   candidates (EC spreadsheet joined to Wikipedia and Wikidata), the 2023 result as a baseline
   with a note where boundaries changed, electorate polls where they exist, enrolment figures.
3. **Election night.** A client for the results XML schema that replays the Electoral
   Commission's demo feed and the 2017, 2020 and 2023 archives at adjustable speed, with a seat
   waterfall from first count through overhang and specials, and that on 7 November points at
   the live `electionresults_2026/xml/` directory polling every 30 seconds.
4. **Campaign data.** Daily advance-voting counts from 26 October, donations over 20k, a
   pollster scorecard against 2020 and 2023 results.

Every data file the app reads is also published as JSON and CSV for anyone to download, with the
Action run that produced it linked. That is the thing no NZ outlet does and the reason to build
this rather than link to them.

## Affected users and systems

NZ voters and politics watchers (readers); Byron (reads the blog, runs the night after the lab
ends); the lab's Pages deployment (`.github/workflows/pages.yml` publishes `site/`); new
scheduled Actions workflows for data refresh; `bin/metrics` (counts the product's PRs and
reviews like any change).

## Constraints

- Static site on GitHub Pages, served under the repo's existing Pages site. No server, no
  database. Data is produced by scheduled Actions jobs that commit JSON into the repo (branch
  and path decided in the spec) and trigger a Pages deploy.
- Only hosts that answered a plain HTTP client in the research are fetched from Actions:
  `electionresults.govt.nz/electionresults_YYYY/xml/**`, the mediademo host, Stats NZ ArcGIS,
  Wikipedia and Wikidata APIs, Polymarket Gamma, data.govt.nz, pollster RSS feeds. elections.nz,
  vote.nz, parliament.nz and the HTML/CSV side of electionresults.govt.nz are behind bot walls:
  fetch once by hand or from Wayback and commit as fixtures with the capture date.
- Licences: attribute Stats NZ (CC BY 4.0) and Wikipedia (CC BY-SA 4.0, the derived poll table
  carries share-alike); attribute and link the Electoral Commission (no CC statement, no claim
  of open licence). Nothing from Policy.nz (derivative works prohibited). RNZ, NZ Herald, Stuff
  and Roy Morgan: link only, never fetch. A descriptive User-Agent with a contact on every
  request; serial requests; honour crawl delays.
- Toolchain matches the lab: Python with uv inline metadata for the pipeline; the front end is
  plain HTML, CSS and ES modules with no bundler unless `node_modules` stays under 150 MB on the
  host. Vendored libraries are committed with their licence file.
- Verifiable by commands and screenshots: every change's definition of done includes a
  command whose output is quoted and Playwright screenshots at a phone and a desktop width.
  Tests cover the allocator against the 2023 quotients fixture, the poll parser against
  committed wikitext, and the XML feed parser against committed demo files.
- Design is a first-class requirement: the frontend-design skill's guidance goes into
  `spec.md` and `AGENTS.md`; the fresh review judges the screenshots.
- No secrets in the repo. The datafinder and PCO keys are not needed for v1; if a later
  milestone needs one, it is a `needs-byron` issue.
- The lab ends 4 November; election night is 7 November. The night client is proven against the
  demo and archives inside the lab, and a handover note tells Byron what to watch on the night.

## Release plan

Days count from 16 October NZ (day 1). Each milestone is live on Pages when it closes.

| Milestone | Closes | Content |
|---|---|---|
| M1 skeleton | day 4 (19 Oct) | Site shell live; hourly poll pipeline; allocator with 2023 fixture; polls and seats view with threshold watch; downloads page |
| M2 v1 usable | day 11 (26 Oct) | Electorate map and 71 pages; coalition explorer; Polymarket overlay; provenance on every number; mobile pass; about and methods page |
| M3 night client | day 17 (1 Nov) | XML replay of demo and archives; seat waterfall; advance-voting daily chart; donations; pollster scorecard |
| M4 harden | day 20 (4 Nov) | Evals green; data workflows proven over several days; handover note for 7 Nov; final post |

Daily iteration between milestones: one shipped change per build day, two when the plan shows
disjoint files.

## Open questions (for the spec)

1. Where data lives: committed to `main` by Actions (interleaves with supervisor pushes) or a
   `data` branch the Pages build checks out. Preferred: the `data` branch.
2. Boundary mismatch: 2023 results were on 2020 boundaries. Show 2023 per voting place re-cut to
   2025 boundaries where places fall inside, or show the old electorate with a note. Preferred:
   the note for v1, re-cut as a later change.
3. Poll average method: simple time-window mean, or house-effect adjustment. Preferred: a
   documented window mean for M1, house effects as a later change with the method published.
4. Map rendering without a bundler: inline simplified GeoJSON (355 KB at 0.001 offset) drawn
   as SVG, or vendored Leaflet with tiles. Preferred: SVG from simplified GeoJSON, no tiles.
5. The 2026 feed ids (`e_no`, `p_no`, `c_no`) do not exist until the night: the client must
   build its id maps from the live reference files at startup.

## Supervisor decisions

1. Accepted 2026-10-17 NZ as the lab's product. Slug `nz-election`; product code under
   `product/nz_election/`; the site under a sub-path of the existing Pages deployment.
2. The spec is written by a Codex job from this intent and the research inventory, guided by
   the frontend-design skill's guidance, and accepted by the supervisor. Concerns flagged in the
   spec are resolved there before the plan job.
3. Concept A, B and C from the research are milestones of one app, not three apps.
