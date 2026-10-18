# NZ Election 2026 specification

## Purpose and decisions

Build a static election app for NZ voters reading on phones before 7 November and on election night. Answer who is winning, by how much, and where the numbers came from. Publish the underlying data.

This specification implements `intent/nz-election/intent.md`. Source references below identify exact rows in `intent/research/nz-election-data-sources.md`. The research is the evidence baseline, dated 16 October 2026; inferred endpoints remain unconfirmed.

Take all preferred answers in the intent: a `data` branch; labelled old-boundary 2023 results; a window mean; SVG from simplified GeoJSON; reference IDs discovered at feed startup. No house-effect adjustment or geographic reallocation in v1.

Milestones: M1 19 October; M2 26 October; M3 1 November; M4 4 November. Each closes only after deployment and verification. The plan must name changes to `.github/workflows/pages.yml`, two new data workflows, and product instructions in `product/nz_election/AGENTS.md`. This design job changes no files.

## Sources and visible licence lines

Codes below are normative shorthand: every requirement using a code inherits its source row and exact visible attribution. Link source names to their original URLs and licence names to the applicable licence. Mixed-source displays show each applicable line.

| Code | Research section and table row | Visible attribution |
|---|---|---|
| P | §5 Wikipedia opinion polling page | "Source: Wikipedia contributors. CC BY-SA 4.0. Parsed and averaged by this project." |
| E | §1 Electorate candidates 2026; Party lists 2026; Enrolment by electorate; 2023/2020/2017 CSVs | "Source: Electoral Commission. Copyright Electoral Commission. No open licence stated." |
| X | §1 Feed reference ids; Media feed demo; Feed schema (observed); Feed public mirror; Night cadence | "Source: Electoral Commission. Copyright Electoral Commission. No open licence stated." |
| G | §3 Stats NZ ArcGIS General Electorates 2025; ArcGIS Māori Electorates 2025; ArcGIS 2020 layers | "Source: Representation Commission, Stats NZ. CC BY 4.0. Boundaries simplified by this project." |
| C | §6 Wikipedia candidates page | "Source: Wikipedia contributors. CC BY-SA 4.0. Candidate information adapted by this project." |
| W | §6 Wikidata candidacies | "Source: Wikidata. CC0." |
| M | §5 Polymarket Gamma | "Source: Polymarket. Subject to Polymarket terms. No open licence asserted." |
| A | §8 Electoral Act 1993 s191; s192; s193; 2023 fixture | "Method: Electoral Act 1993, sections 191-193. Legislation has no copyright. Validation data: Electoral Commission." |
| V | §1 Advance voting stats 2023; Advance voting stats 2026 | "Source: Electoral Commission. Copyright Electoral Commission. No open licence stated." |
| D | §1 Donations over $20k (election year) | "Source: Electoral Commission returns. Copyright Electoral Commission. No open licence stated." |

Do not imply that publicly downloadable EC or market data has an open licence. Keep each source family in separate files. Carry share-alike notices into poll-derived averages, seats and CSVs, and Wikipedia-derived candidate tables. Preserve contributor-history and revision links.

## Numbered requirements

Verification commands are specified interfaces for the builder to implement, not claims that tests already exist or passed. Their exact contracts appear under Testing.

### Polls and seats

1. **[M1] Current seat picture.** Show a proportional seat strip first, party seat counts, majority requirement, averaging dates, and the electorate assumptions used. Distinguish calculated seats from a forecast of winners. Sources P+A; show P+A attribution. Verify `verify.py polls` prints `PASS polls`; phone and desktop screenshots must show the strip above the poll history.
2. **[M1] Poll history and average.** Include all published 2026 party-vote polls present in the source revision, retain original references, and separate national party-vote rows from electorate, Māori-roll, preferred-PM and event rows. Publish the window method below and a dated trend series. Source P; show P attribution. Verify `verify.py polls` and committed-wikitext parser tests.
3. **[M1] Threshold watch.** Show each named party averaging 2-7%, including a party in that range in any included poll. Mark 5% and whether the selected electorate assumptions allow qualification below it. Missing values are not zero. Sources P+A; show P+A attribution. Verify `verify.py thresholds` prints `PASS thresholds`; screenshot must include text labels independent of colour.
4. **[M2] Coalition explorer.** Let readers select parties, edit electorate assumptions, and compare their total with `floor(occupied_house / 2) + 1`. Label this "Seats needed for a majority", not proof that a government will form. Do not preselect a politically predicted coalition. Sources P+A; show P+A attribution. Verify `verify.py coalitions` prints `PASS coalitions`, including overhang and list-vacancy cases.
5. **[M2] Markets alongside polls.** Display event wording, outcome, quoted price as a percentage, liquidity or volume with its supplied unit, resolution criteria link, and observation time. Separate next-PM, government-membership and seat-band contracts. Do not turn their prices into poll shares or combine unrelated contracts. Source M; show M attribution. Verify `verify.py markets` prints `PASS markets`; screenshots show "Market price", never "Poll".

### Electorates

6. **[M2] Map and directory.** Provide 64 general and seven Māori electorates, separately selectable, using 2025 polygons. Search names with and without macrons. Every map selection has an equivalent ordinary directory link. Source G; show G attribution. Verify `verify.py geography` prints `PASS geography: 64 general, 7 Māori`; inspect both map screenshots.
7. **[M2] Candidate pages.** Generate 71 stable pages. EC supplies official names and party affiliation; Wikipedia and Wikidata add cited list ranks and identity links. Join through explicit reviewed mappings, never surname alone. Preserve unresolved conflicts for review. Sources E+C+W; show their attribution beside the relevant fields. Verify `verify.py candidates` prints `PASS candidates: 71 electorates`; no assumption that spreadsheet rows, unique people and candidacies have equal counts.
8. **[M2] Baselines and local information.** Show 2023 party and candidate votes under their original electorate names, local polls where published, and captured enrolment figures with their actual observation dates. Changed or successor electorates show individually identified old-electorate comparisons, never invented 2025 totals. Sources E+G+P; show all applicable attribution. Verify `verify.py electorates` prints `PASS electorates: 71 pages`; screenshots include changed-boundary and missing-data cases.

### Election night

9. **[M3] Replay and live modes.** Parse committed demo and 2017/2020/2023 archive fixtures. Replay recorded sequences at 1x, 10x and 60x, with pause and reset. A lone final archive is a final snapshot, not an authentic time series. Discover live reference IDs before accepting results; poll in the browser no more frequently than every 30 seconds. Source X; show X attribution and a persistent mode label. Verify `verify.py night` prints `PASS night`; test malformed XML, changed IDs and stale feeds.
10. **[M3] Count and seat changes.** Show party vote, seats, electorate leaders and voting places counted. Never label percentage of places as percentage of votes. Separate proportional entitlement, overhang and later official-result changes; show specials only when the source supports that decomposition. Sources X+A; show X+A attribution. Verify `verify.py waterfall` prints `PASS waterfall`; inspect replay and unavailable-live screenshots.

### Campaign data

11. **[M3] Advance voting.** Show national daily counts and cumulative totals from 26 October when a verified capture exists. No electorate breakdown. Source V; show V attribution. Verify `verify.py advance` prints `PASS advance`, including non-cumulative input and missing-day fixtures.
12. **[M3] Donations and pollster record.** Show disclosed donations over $20,000 with receipt and disclosure dates where available; explicitly exclude an inference of total funding. Compare each pollster's final eligible national poll before the 2020 and 2023 elections with official party shares, publishing per-party percentage-point errors and coverage. Poll data comes from pinned historical Wikipedia revisions with the same P licence obligations. Sources D+P+E; show applicable attribution. Verify `verify.py campaign` prints `PASS campaign`; no score when comparable input is absent.
13. **[M4] Handover.** Document startup, source switching, stale-data diagnosis, rollback, unresolved source gaps and the 27 November official-results transition. Sources X and the §1 media documentation row; show X attribution wherever copied data appears. Verify `verify.py handover` prints `PASS handover`; supervisor reviews the runbook before 4 November.

### Data and publishing

14. **[M1, extended M2-M3] Downloads and provenance.** Every published dataset has JSON and CSV, original source links, acquisition time, observation date, licence, transformations and producing Action run. Every displayed number resolves to its dataset row or calculation inputs. Sources P/E/X/G/C/W/M/A/V/D as applicable; show the corresponding attribution on downloads and displays. Verify `verify.py provenance` prints `PASS provenance`.
15. **[M1] Refresh and resilience.** Hourly and daily workflows retain last-good source bundles on failure, publish explicit status, and trigger the existing Pages publisher. Sources and attribution follow each bundle. Verify `verify.py pipeline` prints `PASS pipeline`, including partial failure, no previous data, concurrent writers and failed deployment.
16. **[M4] Release quality.** All source-derived UI retains its attribution; all routes pass accessibility, static-data and screenshot checks below. Verify `verify.py all`, `uv run --with pytest pytest -q`, `bin/lint` and the screenshot command. Record actual outputs in implementation reviews.

## Poll method and assumptions

Use an inclusive 30-calendar-day window ending on the displayed NZ date, selected by fieldwork end date. Each distinct national poll receives equal weight. Deduplicate revisions of the same poll; retain the latest corrected row and its history. Do not use publication date when fieldwork end is available.

Average only a coherent party vector: every named party reported by any window poll must be explicitly represented in every included poll. A newly separated party requires a reviewed source mapping or exclusion of incompatible rows, disclosed with reasons. Never fill an unreported party with zero or silently renormalise a published poll. Exception (supervisor, 2026-10-18, judgement call of 10:4xZ, no reply by its 22:45Z deadline; Byron 21:44Z "merge freely"): when a poll names every party but leaves "Others" blank, "Others" is derived as 100 minus the sum of the named parties for that row only, when that remainder is between 0 and 10 points; the row is labelled derived on /polls/ and the method page names the rule and the affected pollsters. No named party is ever derived. Retain "Others" in the denominator but do not award seats to an aggregate category.

For an incomplete vector, publish available descriptive shares and withhold the seat calculation with an explanation. Store shares as exact decimal-derived integers with a common scale. Publish included poll IDs, exclusions, denominator, method version and rounding policy. Round only displayed percentages.

M1's initial electorate scenario uses the 2023 party electorate totals from the fixture, explicitly labelled "2023 electorate seats assumed; 2026 has different boundaries". It leaves unassigned electorates unprojected, does not assert a 2026 winner map, and is editable in M2. A party's electorate wins cannot exceed its supplied candidate capacity. If verified 2026 list capacity is unavailable, label the result "List capacity not checked" rather than claiming a complete s193 prediction.

## Allocator contract

Implement the same pure algorithm in Python for publication and ES modules for interaction; use shared golden inputs to prove parity. No copied unlicensed implementation.

`allocate({partyVotes, electorateWins, lists, electorateWinners, nonListWinners, baseSeats:120, tieOrder}) -> {entitlements, listMembers, seats, overhang, vacancies, occupiedHouse, quotients, unresolvedTies}`

Party votes are non-negative exact integers, including excluded parties in the denominator. Lists are ordered candidate IDs; electorate winners are candidate IDs. `nonListWinners` identifies independent and unlisted-party winners. Validate unique candidates, consistent counts and total electorate wins.

Apply s191 qualification: at least 5% of all valid party votes, or an electorate win for a party with a qualifying list. Award the highest `120 - nonListWinners.length` quotients using odd divisors 1, 3, 5... . Compare rational numbers by integer cross multiplication. Do not use rounded percentages or floating-point quotient ordering.

Apply s192: retain all electorate wins; list-seat entitlement is `max(entitlement - electorateWins, 0)`. Overhang is the sum of positive `electorateWins - entitlement`. Apply s193: fill lists in order, skipping electorate winners; exhausted lists leave vacancies, never redistribute them. `occupiedHouse = 120 + overhang - vacancies`, including non-list winners.

Ties require an externally supplied recorded lot result in `tieOrder`; without one, return the unresolved allocation boundary and suppress a definitive seat total. Do not resolve ties alphabetically or randomly inside the pure function.

### Required 2023 golden fixture

Use the official final pre-Port Waikato result: **2,851,211 valid party votes, 120 proportional seats, two overhang seats, House 122**.

| Party | Party votes | Electorate seats | Entitlement | List seats | Occupied seats | Last winning quotient |
|---|---:|---:|---:|---:|---:|---|
| National | 1,085,851 | 43 | 48 | 5 | 48 | 1,085,851 / 95 |
| Labour | 767,540 | 17 | 34 | 17 | 34 | 767,540 / 67 |
| Green | 330,907 | 3 | 15 | 12 | 15 | 330,907 / 29 |
| ACT | 246,473 | 2 | 11 | 9 | 11 | 246,473 / 21 |
| NZ First | 173,553 | 0 | 8 | 8 | 8 | 173,553 / 15 |
| Te Pāti Māori | 87,844 | 6 | 4 | 0 | 6 | 87,844 / 7 |

The remaining parties total 159,043 votes and receive no seats; TOP's displayed 2.22% does not qualify. Commit the full official per-party votes, lists and `party-quotients.csv`, not a fabricated aggregate substitute. The inventory does not enumerate those remaining exact votes or every quotient: capture them from the identified official/Wayback sources before accepting the fixture.

Compare all 120 selected quotient fractions and their ordering with the official file, accounting for its display precision. The last winning quotient is Green `330907/29`; the highest losing quotient is National `1085851/97`. Do not incorporate the later by-election House of 123.

Edge tests: exactly 5%; just below 5% with and without an electorate win; excluded votes retained in the denominator; independent and unlisted winners reducing 120; multiple overhang parties; exhausted lists; electorate winners skipped in lists; exact ties at the cutoff; zero votes and invalid inputs; scaled equivalent inputs; Python/JS parity.

## Data pipeline and file contracts

Use two scheduled workflows on `main`: `nz-election-hourly.yml` at minute 17 each hour and `nz-election-daily.yml` at 15:43 UTC daily. Both also support manual dispatch. Schedules are best effort, not a real-time guarantee. No election-night polling workflow.

Python uses uv inline metadata, stdlib HTTP/JSON/XML/CSV where practical, and small pinned parser dependencies when necessary. Requests are serial, bounded by timeouts and retries, honour `Retry-After` and crawl delays, and use `unattended-lab/0.1 (https://github.com/byronxlg/unattended)` where the client permits. Never fetch prohibited hosts automatically or send credentials.

Store published data at `product/nz_election/data/` on a dedicated `data` branch. That branch holds generated artifacts and manifests, not a divergent copy of application code. Jobs execute code checked out from a pinned `main` SHA and record that SHA.

Every JSON uses this envelope, with source arrays for mixed inputs:
```json
{"schema_version":1,"source":[{"id":"P","url":"https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_New_Zealand_general_election","revision":"123","licence":"CC-BY-SA-4.0"}],"fetched_at":"2026-10-17T01:17:00Z","run_url":"https://github.com/byronxlg/unattended/actions/runs/123","code_sha":"abc","data":[]}
```
`fetched_at` means the input acquisition time, not the rebuild time; retain older timestamps for unchanged/manual inputs. Each row has `id`, `source_ref` and an observation date or source update time. Mixed acquisitions retain per-source timestamps. Derived files add `input_hashes`, `method_version` and `generated_at`.

| Job | Inputs | JSON outputs relative to data root; abbreviated payload |
|---|---|---|
| Hourly polls | P pinned revision, wikitext and reviewed mappings | `polls.json`: `[{id,fieldwork_start,fieldwork_end,pollster,sample,shares,reference_urls}]`; `averages.json`: `[{date,shares,poll_ids,excluded_ids}]`; `seats.json`: `{assumptions,entitlements,seats,overhang,vacancies,occupied_house}`; `electorate-polls.json`: `[{electorate_id,poll_id,shares}]` |
| Hourly markets | M explicit allowlisted event slugs | `markets.json`: `[{event_id,question,outcomes:[{name,price}],volume,volume_unit,resolution_url,updated_at}]` |
| Daily geography | G simplified 2025 layers; committed reviewed 2020 correspondence | `boundaries-general.json`, `boundaries-maori.json`: GeoJSON FeatureCollections with the common envelope as foreign members; `electorates.json`: `[{id,name,kind,slug,baseline_ids,boundary_note}]` |
| Daily candidates and baseline | E captured XLSX/PDF/CSV/enrolment; C revision; W claims | `candidates.json`: `[{id,name,party_id,electorate_id,list_rank,wikidata_id,field_sources}]`; `party-lists.json`: `[{party_id,candidate_ids}]`; `baseline-2023.json`: `[{old_electorate_id,party_votes,candidate_votes}]`; `enrolment.json`: `[{electorate_id,as_of,enrolled,eligible}]` |
| Daily campaign | Reviewed V/D captures; pinned historical P and E fixtures | `advance-voting.json`: `[{date,daily,cumulative}]`; `donations.json`: `[{id,party,donor,amount_nzd,received_date,disclosed_date,document_url}]`; `pollster-scorecard.json`: `[{year,pollster,poll_id,party_errors,mean_absolute_error,coverage}]` |
| Daily replay packaging, M3 | Committed X archive/demo captures and capture manifests | `night/index.json`: `[{sequence_id,mode,snapshot_paths}]`; `night/<sequence>/<timestamp>.json`: `{reference_version,statistics,party_results,electorate_results}` |

Each scheduled workflow has one refresh job running its stages serially, then one publication job. Source bundles validate atomically: poll history, averages and seats advance together. Unrelated successful bundles may publish despite another bundle failing.

Generate CSV siblings for every JSON, including index/status files; flatten nested collections into documented rows, repeating provenance columns. Boundary CSVs contain ID, name, kind and `geometry_json`. Do not silently drop geometry or list members.

Publish `status.json` with the same envelope and entries such as `{"dataset":"polls","state":"stale","last_attempt_at":"...","last_success_at":"...","last_good_run_url":"...","error_code":"parse_drift"}`. A failed first fetch has state `unavailable` and null success time, never an empty dataset disguised as success. Publish `manifest.json` listing all JSON/CSV paths, hashes, licences, counts and producing runs; exclude its own hash to avoid recursion.

On failure, keep last-good bytes and timestamps; write status and an Action summary with a non-zero refresh outcome. A publication step running after handled refresh failures must still publish status. Retry transient failures with a small bounded backoff; do not retry authentication or bot challenges indefinitely.

Manual captures live in fixtures with original URL, archive URL if used, captured time, SHA-256 and reviewer. Daily jobs ingest new committed captures; they do not defeat bot walls. Absent advance-voting, donations or enrolment captures remain visibly unavailable or dated.

### Deployment and concurrency

Both writers share a non-cancelling publication concurrency group. Immediately before committing, fetch the latest `data` tip and apply only the validated source bundles owned by that run; retry a non-fast-forward push against the new tip. Never overwrite the other cadence's files.

Extend `pages.yml` with `workflow_run` completion triggers for the two exact workflow names, retaining `main` push and manual dispatch. A `GITHUB_TOKEN` push alone must not be assumed to trigger another workflow. Ignore untrusted branches and unrelated runs; never execute code from the data checkout.

Pages checks out trusted `main` code and the latest complete `data` commit separately, pins both SHAs in its build manifest, and keeps current blog check, metrics and build steps. Then run the product build before uploading `site/`. Preserve `/unattended/`, posts, metrics, feed and blog about routes.

A failed product validation blocks deployment; the previous Pages deployment remains live. Avoid cancelling active deployments repeatedly: serialize Pages publication and allow pending builds to coalesce. Document restore-by-pinned-code-and-data-SHA through manual dispatch. M1 bootstraps the data branch before enabling schedules.

## Site and directory layout

Base URL: `/unattended/nz-election/`. Navigation labels: "Polls and seats", "Electorates", "Election night", "Campaign", "Downloads", "About and methods".

| URL suffix | Page |
|---|---|
| `/` | Polls and seats |
| `/electorates/` | Map and searchable directory |
| `/electorates/<slug>/` | One of 71 electorate pages |
| `/night/` | Replay and live desk |
| `/campaign/` | Advance voting, donations and pollster record |
| `/downloads/` | Dataset catalogue and run history links |
| `/methods/` | About, methods, assumptions and licences |

Slugs come from a committed ID-to-slug registry; display names retain macrons. Do not derive URLs from mutable names on every refresh.

```text
product/nz_election/
  AGENTS.md
  pipeline/           fetch, parse, validate, allocate, export, build, verify
  fixtures/           wikitext, EC captures, XML, quotients, geography, manifests
  tests/              unit, parity, pipeline and browser checks
  web/                HTML templates, CSS, ES modules, icons
  config/             source registry, joins, slugs, party colours, feed URLs
  runbook.md
```

`uv run product/nz_election/pipeline/build.py --data <checkout>/product/nz_election/data --out site/nz-election` copies `web/` assets, renders static tables into all pages and copies data to `site/nz-election/data/`. It never writes outside its output subtree. All links respect the Pages prefix. Use plain HTML, CSS and ES modules; no bundler, runtime third-party library, map tiles or font CDN. Vendored runtime library size: zero.

Query ArcGIS in WGS84 with `maxAllowableOffset=0.001`; general boundaries are approximately 355 KB versus 21.3 MB at full detail. Fetch the seven Māori features separately and measure their simplified size. Do not download full-detail geometry routinely. Use a small local SVG projection with explicit longitude unwrapping for islands crossing the antimeridian.

## Design

Apply the frontend-design skill and the repository Design rules in product instructions. Direction: ballot-paper clarity, the Commission campaign's orange as a restrained interaction cue, and the proportional seat strip as the dominant visual. The app is independent, not an official Commission service.

Core tokens: `paper #FFFFFF`, `ink #181818`, `muted #595959`, `surface #F0F2F4`, `vote-orange #F58220`, `focus-blue #005EA8`. Use one light theme. Orange gets dark text and an ink boundary when necessary; never small orange text on white.

Party fills are a separate semantic set: National blue `#00529F`, Labour red `#D82C20`, Green `#098137`, ACT yellow `#FDE401`, NZ First black `#000000`, Te Pāti Māori red `#B2001A`, and Opportunity purple `#6B3FA0`. Treat these as candidate identity samples until the builder records dated evidence from each party's own logo or official identity material in `config/party-colours.json`; Wikipedia chart colours are not identity authority. Other parties receive verified identity samples or a labelled neutral pattern. Do not redistribute logos.

Use `"Arial", "Helvetica Neue", sans-serif` throughout: compact ballot-like labels and familiar, unembellished tables. No downloaded font files. Tabular numerals for data, normal prose elsewhere. Type scale: 14px attribution, 16px body, 20px subsection, 28px page title, 40px seat emphasis; line-height 1.5 for prose and 1.15 for large labels. Keep prose below 72 characters per line.

Use 16px phone gutters, 32px desktop gutters, 8px spacing increments and a 1120px maximum width. Left-align text and labels; right-align numeric table columns and decimals. No justified text. At 800px, introduce a two-column main/support layout. Borders only distinguish rows, controls, thresholds or geographic boundaries. No repeated cards, shadows, tracked capitals or entry animations.

The one memorable element on each page is its data: the seat strip on polls; country silhouette on the directory; selected electorate outline on detail; seat-change waterfall on night; cumulative advance-vote curve on campaign. Downloads uses the file inventory as its dominant element; methods uses a worked seat calculation. Supporting charts remain visually quiet.

```text
Polls, phone                    Polls, desktop
[Navigation wraps]              [Navigation]
[Seats from current polls]      [Seats from current polls                 ]
[Proportional strip]             [Proportional strip with majority marker  ]
[Party seats | source]           [Party seats + trend       | Assumptions ]
[Threshold watch]               [Threshold watch           | Coalition   ]
[Trend / poll table]             [Poll history              | Markets     ]
[Assumptions / coalition]
[Markets / source]

Electorates, phone              Electorates, desktop
[Search electorate]             [Search / general / Māori]
[General | Māori]               [NZ outline map          | Name directory]
[NZ outline map]                [Selected summary        | Source        ]
[Name directory / source]
Detail:                         Detail:
[Name / boundary note]          [Name / boundary note]
[Electorate outline]            [Outline       | Candidates and sources  ]
[Candidates / sources]          [2023 baseline | Local polls / enrolment ]
[2023 / local polls / roll]

Night, phone                   Night, desktop
[Replay / live / time]           [Replay / live / time / pause / speed]
[Places counted]                [Places counted       | Source status     ]
[Seat waterfall]                [Seat waterfall                          ]
[Party table]                   [Party table          | Electorate leaders]
[Leaders / source]               [Replay timeline      | Assumptions       ]

Campaign, phone                Campaign, desktop
[Advance votes / date]          [Advance votes / date]
[Cumulative curve]             [Cumulative curve      | Daily counts      ]
[Daily counts / source]         [Donation table                           ]
[Donations table]              [Pollster comparison   | Method / sources  ]
[Pollster comparison]

Supporting pages, phone        Supporting pages, desktop
[Downloads or methods]         [Downloads or methods]
[File list or worked example]  [File list or worked example | Licence/index]
[Licence / run / method]       [Run links and detailed method             ]
```

Design critique before implementation: a generic dashboard grid would bury the seat answer and repeat containers. Replace it with a single full-width proportional strip and aligned party rows. Do not enlarge a standalone number at the expense of party composition. A 120-seat base is visibly distinct from appended overhang; label the actual House and majority when they differ.

## Provenance and downloads

Render a shared `source-note` component at every numeric group, with row-level references where sources or dates differ. SVG accessible descriptions and table captions point to it. A calculation includes links to its inputs and method, not merely "Source: this project".

```html
<td aria-describedby="source-poll-123">32.4%</td>
<p class="source-note" id="source-poll-123">
  <a href="SOURCE_REVISION_URL">Wikipedia contributors, poll row 123</a>.
  Fieldwork ended <time datetime="2026-10-12">12 October 2026</time>.
  Retrieved <time datetime="2026-10-17T01:17:00Z">17 October, 2:17 pm NZDT</time>.
  <a href="LICENCE_URL">CC BY-SA 4.0</a>. Adapted.
  <a href="RUN_URL">Data run</a>.
</p>
```

Store ISO timestamps in UTC; render with `Pacific/Auckland`, including NZST/NZDT. Never confuse the latest fetch with when a poll was conducted or votes counted. Mark hourly datasets overdue after three hours, daily jobs after 36 hours, and live requests stale after 90 seconds without a successful response. Show source update age separately; unchanged source content is not automatically a failed fetch.

Downloads enumerates every published JSON and CSV from the manifest, including geometries, assumptions, status and replay snapshots. Show size, hash, licence, observation range, retrieval time and producing run. Link immutable data-commit versions as well as current files; do not rely on expiring Actions artifacts.

Live browser results need explicit treatment: offer local JSON/CSV exports with original XML URLs, source timestamps, browser retrieval time and application build run. Label the producer "This browser"; never claim an Action produced live bytes. This exception to the all-files-have-a-producing-Action rule requires supervisor acceptance below.

## Election-night operation

Fetch `electorates.xml`, `parties.xml` and `candidates.xml` as one validated reference version before `election.xml`. Validate expected 2026 electorate counts, candidate references and list IDs. Do not assume sequential directory names or reuse 2023 IDs. Derive detail URLs from validated source IDs.

Fetch only national totals and the currently selected electorate, serially; never fetch 71 detail files every 30 seconds. Pause background polling in hidden tabs, resume with a fresh request, prevent overlapping polls, and back off on errors. Retain the last complete snapshot with a visible stale label; never merge incompatible reference versions.

Start in replay mode before the election. Configure HTTPS candidate feed roots, including the preliminary directory, with explicit availability checks; do not assume the final directory exists on the night. Browser CORS must be tested separately from a successful HTTP client fetch. Browser requests cannot set a custom User-Agent: use normal browser identification and document this exception.

If direct browser access fails, show the last packaged snapshot and a link to the official results site. Do not silently label demo data live or add an unapproved proxy. Archives with no time sequence show only their final snapshot; any teaching sequence constructed from them is explicitly "Illustrative replay".

## Accessibility and quality

Use semantic headings, landmarks, skip navigation, labelled controls and visible 3px blue focus outlines with white separation. Controls have at least 44px touch targets. Interactive charts must also have tables; do not require hovering, dragging or distinguishing colours.

Normal text meets WCAG AA 4.5:1; large text and meaningful graphical boundaries meet 3:1. Party fills never carry the sole distinction: use names, counts and outlines or patterns. Keep text outside coloured segments in ink on white, especially ACT yellow and adjacent red parties. Verify all actual colour pairings.

Respect reduced motion; no automatic decorative animation. Replay starts paused. Announce requested updates concisely with a polite live region rather than reading an entire refreshed table. Keyboard users can select electorates from the directory without traversing every SVG path.

Generate all published tables, source notes and dataset links at build time. With JS disabled, polls, candidate pages, campaign tables and replay snapshot tables remain readable; interactive controls explain that they require JavaScript. At 390px there is no page-wide horizontal overflow; wide data tables may have labelled local scroll containers.

## Testing and acceptance

All commands run from repository root. The plan must implement these interfaces, keep network-dependent smoke tests separate from deterministic tests, and quote real output at release. Never treat these expected strings as observed results.

| Command | Expected result |
|---|---|
| `uv run --with pytest pytest -q product/nz_election/tests/test_allocator.py` | Exit 0; all fixture and edge tests pass, including every official winning quotient and House 122 |
| `uv run --with pytest pytest -q product/nz_election/tests/test_poll_parser.py` | Exit 0; pinned wikitext parses; event rows, footnotes, merged cells, changed headers and malformed rows are covered |
| `uv run --with pytest pytest -q product/nz_election/tests/test_xml_parser.py` | Exit 0; committed demo/archive files parse; unknown IDs, absent fields, inconsistent totals and malformed input are rejected |
| `uv run --with pytest pytest -q product/nz_election/tests/test_geojson.py` | Exit 0; 64+7 IDs preserved, rings closed, finite WGS84 coordinates, no empty polygons, valid antimeridian handling |
| `uv run product/nz_election/pipeline/verify.py <check>` | Exact `PASS <check>` line, with count suffixes specified in requirements; non-zero on failure |
| `uv run product/nz_election/pipeline/verify.py all` | Individual check lines followed by `PASS all` |
| `uv run --with pytest pytest -q` | Exit 0 and pytest summary with actual counts |
| `bin/lint` | Exit 0; preserve existing output contract |
| `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots` | `PASS screenshots: 77 routes, 154 baseline images` at M4; additional state screenshots listed separately |

Geography tests compare simplified output with a committed reference fixture for retained IDs, island components, extents and representative interior points; allow at most 1% aggregate area change using the same documented projection. Investigate failures rather than increasing tolerance. General geometry should remain below 500 KB; measure and set a separate Māori budget before M2.

The Playwright script serves `site/` locally under `/unattended/`, discovers the 77 product routes, screenshots each at 390x844 and 1280x800, checks broken local links and console errors, and writes route-labelled PNGs plus a manifest. Reuse installed Chromium or install Chromium only in CI. No Docker or broad browser downloads.

Additional browser cases cover keyboard navigation, JS disabled, reduced motion, source disclosure, threshold changes, stale/unavailable feeds, changed-boundary pages, replay and coalition edits. Capture these states separately from the 154 baseline images. The builder must inspect screenshots, and fresh review must assess bugs, security and compliance in REVIEW.md order.

## Concerns

Every item below is **for the supervisor to accept or change before planning**.

- **Wikipedia table drift:** Headers, footnotes and templates can change silently. Resolve with revision-pinned fixtures, semantic column checks, row-count/change diagnostics and atomic last-good retention; never quietly omit unexplained rows.
- **Pages frequency and quota:** Hourly publication plus daily work and lab pushes may delay deployment or exceed available minutes/storage. Start with two cadences and coalesced Pages builds; measure actual usage for several days. If limits require a slower public refresh, obtain a recorded scope decision and display the true cadence.
- **Share-alike:** The derived poll table and adapted candidate content need CC BY-SA attribution, revision history and notices. Keep source families separate and publish poll-derived outputs under CC BY-SA 4.0; do not imply this relicenses unrelated EC material.
- **2026 feed IDs and directory:** IDs and preliminary/live paths remain unknown. Resolve by startup references and configuration, with 71-electorate validation; never hardcode historical IDs.
- **XML WAF exemption and CORS:** HTTP availability does not prove browser access. Probe from the deployed origin before M3. If the exemption closes or CORS prevents access, use a clearly dated static fallback; live mode remains unavailable unless the supervisor approves a feasible alternative architecture.
- **Browser identification and live exports:** Browsers cannot send the requested custom User-Agent, and live browser bytes have no producing Action run. Accept the browser-specific exceptions above, with honest provenance, or change the static/live requirement.
- **Replay evidence:** Final archives do not establish count-by-count history or a specials decomposition. Use recorded demo sequences, final archive snapshots and explicitly illustrative replay; do not invent historical observations.
- **Blocked daily sources:** Advance voting, donations and enrolment depend on manual captures; the expected 2026 advance CSV URL is inferred. Daily processing does not guarantee daily new source data. Accept dated/unavailable displays and assign capture responsibility before the lab ends.
- **EC and market redistribution:** Attribution is not permission. Preserve the stated limitations, publish no unnecessary document reproductions, and have the supervisor confirm the proposed normalized downloads before those sources ship.
- **Incomplete 2023 fixture:** The inventory gives exact major-party totals but not every excluded-party vote or quotient row. Require the full official capture before allocator acceptance. A read-only curl attempt during this design run exited 6 with no response, so no new endpoint verification is claimed.
- **Poll comparability and seat assumptions:** "Others", missing party columns, boundary changes and list capacity can alter allocation. Accept conservative vector validation, explicit exclusions and labelled electorate assumptions; do not present this as a probability forecast.
- **Candidate joins and list capacity:** Source row counts differ and names can collide. Resolve through reviewed identity mappings and captured party lists; withhold unsupported joins and mark unchecked capacity.
- **Party identity colours:** Candidate hex values require evidence from parties themselves. Record that evidence during implementation and adjust values before screenshot acceptance; retain accessible external labels.
- **Election-night ownership:** The lab ends three days before polling day, and official results follow later. Assign Byron the runbook, feed checks and manual captures by M4; do not promise unattended recovery or post-lab archival collection.

## Out of scope

Policy.nz content and derivative policy comparisons are excluded because its terms prohibit the proposed reuse. Hansard, parliamentary voting records and written questions do not answer the four primary views and introduce blocked or maintenance-sensitive sources. Census profiles remain excluded until a licensed, accessible source on 2025 boundaries clears review.

Also exclude house-effect models, probabilistic forecasts, geographic reallocation of 2023 votes, uniform-swing predictions, unverified coalition-exclusion claims, candidate photos, map tiles, trading, accounts, a backend and automatic archiving of every browser live snapshot. These would add unsupported assumptions or operations beyond a small, verifiable static app.
## Supervisor resolutions

Accepted by the supervisor (Claude) 2026-10-17 NZ (day 2), job `spec-nz-election` (read-only,
339 s, thread 01a144a8). The text above is Codex's as delivered, punctuation normalised. Where a
resolution below changes a requirement, the resolution wins.

### Scope by milestone (the plan follows this, not the bracketed tags above)

- M1 (day 4, 19 Oct): one page that answers the question, and the pipe that feeds it.
  Requirements 1, 2, 3 and 14 on the polls page; `/downloads/` and `/methods/` as real pages
  with the catalogue and the worked 2023 calculation; `/electorates/`, `/night/`, `/campaign/`
  as one-paragraph placeholders in the navigation (so routes and screenshots are stable). The
  allocator with the full 2023 golden fixture. The hourly workflow only (requirement 15 is
  hourly at M1, daily at M2); the `data` branch; the `pages.yml` change. Screenshots of every
  route at both sizes. Nothing else.
- M2 (day 11, 26 Oct): 4, 5, 6, 7, 8, daily workflow, geography budget.
- M3 (day 17, 1 Nov): 9, 10, 11, 12. M4 (day 20, 4 Nov): 13, 16, 77-route screenshot count.

### Decisions on the concerns

1. Wikipedia table drift: accepted as written. Revision-pinned wikitext fixture committed under
   `fixtures/`; the parser's tests run against the fixture, the hourly job against the live
   revision, and an unexplained row count change sets `parse_drift` and keeps last-good.
2. Pages frequency: accepted. Two cadences, coalesced Pages builds, measure for several days
   and report minutes in the daily post. Lab pushes to `main` already trigger Pages; that is
   the third writer and the concurrency group must include it.
3. Share-alike: accepted. Poll-derived JSON and CSV and the candidate tables carry
   CC BY-SA 4.0 in the envelope and on the page; EC-derived files carry the EC line. A
   `LICENCES.md` at the data root states this per source family.
4. 2026 feed IDs: accepted, M3.
5. XML WAF and CORS: accepted. The supervisor probes CORS with Playwright from the deployed
   origin before M3 starts. No proxy; if the browser cannot fetch, live mode shows the dated
   packaged snapshot and a link to the official site.
6. Browser identification and live exports: both exceptions accepted with the stated
   provenance ("This browser"). Requirement 14's "producing Action run" reads "producing run
   or browser" for live exports only.
7. Replay evidence: accepted. Demo sequence for replay; archives are final snapshots;
   constructed sequences are labelled "Illustrative replay".
8. Blocked daily sources: accepted. Capture responsibility during the lab is the supervisor,
   who runs `curl` locally (read-only) and commits captures under `fixtures/` with the manifest
   fields the spec names; after 4 Nov it is Byron, through the M4 handover. Missing captures
   display as dated or unavailable, never as zero.
9. EC and market redistribution: confirmed. Ship normalised rows (JSON, CSV) with the EC
   attribution line; never reproduce EC PDFs, XLSX or market pages. Polymarket rows carry the
   quoted terms line and the observation time.
10. Incomplete 2023 fixture: accepted. The supervisor captures the official 2023 per-party
    votes, lists and party quotients file from electionresults.govt.nz before the M1 build is
    dispatched and commits them with SHA-256 and URL. The allocator test asserts against the
    captured file; the table in the spec is a cross-check, not the fixture.
11. Poll comparability and seat assumptions: accepted as written, including withholding the
    seat calculation on an incomplete vector with the explanation on the page.
12. Candidate joins and list capacity: accepted, M2.
13. Party identity colours: the candidate values ship in M1 with `"evidence": null` in
    `config/party-colours.json` and the UI never carries meaning by colour alone, so nothing
    depends on them. The supervisor supplies evidence captures before M2 screenshot acceptance.
14. Election-night ownership: accepted. M4 opens a `needs-byron` issue with the runbook, the
    feed checks and the capture list. The lab promises nothing after 4 Nov.

### Constraints the spec did not know

- The Codex sandbox has no network (the design run's `curl` exited 6, DNS failure). Every
  input a build needs is a committed fixture; builds never fetch. Fetching happens in two
  places only: the Actions workflows, and the supervisor's local read-only captures.
- The `data` branch is bootstrapped by the hourly workflow on its first run (create an orphan
  branch if absent), not by a local push. Nobody pushes product data from a machine.
- Workflows run the code of the `main` checkout that triggered them and record `GITHUB_SHA`;
  "pinned main SHA" means that, not a separate pin to maintain.
- `product/nz_election/AGENTS.md` holds product-specific rules; the root `AGENTS.md` stays
  under a page and points at it.
- Verification counts for M1 are set in the plan (routes, images, tests); the 77 and 154 are
  M4 numbers.

### Design, checked against the frontend-design skill and AGENTS.md

Accepted with three changes. (a) The type stack is a deliberate choice, not a default: the
no-download constraint and the ballot-paper reference justify a system sans, and the plan
records that reasoning in `methods`. Tabular numerals are mandatory wherever numbers align.
(b) The seat strip is the hero and the type is part of it: party seat counts sit in the strip
at the 40 px size, no separate headline number above it, no "Seats from current polls" eyebrow
beyond the page title in sentence case. (c) Copy is written for a voter: "Seats needed for a
majority", "Last poll ended 12 October", "Updated 2:17 pm, Friday". No "this project" as a
source; every calculation links its inputs. The generated-page tells in AGENTS.md apply;
the orange-on-white rule (dark text, ink boundary) stands. Screenshots at 390x844 and
1280x800 are part of every definition of done and the fresh review judges them.
