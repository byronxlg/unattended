# NZ election M2 implementation plan

## Scope and working rules

Implement requirements 4, 5, 6, 7 and 8, the daily workflow and geography budgets by 26 October. Supervisor resolutions in `spec.md` override its body. M1 is shipped in PRs #9, #10 and #11; unchecked boxes in the old plan do not mean unfinished work.

Work in the supplied `change/*` worktree, one increment per PR. Commit locally; the supervisor reviews and merges. Never push locally or write the `data` branch outside Actions. This plan authorizes changes to `.github/workflows/nz-election-daily.yml`, `nz-election-hourly.yml` and `pages.yml`, alongside product code, tests, configuration and runbook. Leave unrelated files alone.

All builds and deterministic tests are offline. Python runtime remains standard-library-only, with uv inline metadata. No bundler, runtime libraries, downloaded fonts, map tiles or backend. Captures are supplied and committed by the supervisor before dispatch. The daily workflow processes committed captures; it does not acquire upstream data.

This is a planning deliverable based on repository inspection. Commands and PASS lines below are acceptance contracts, not observed results.

## Shipped foundations and required changes

Reuse `allocator.py`, `allocator.mjs`, exact window means, immutable captures, JSON/CSV envelopes, directory exchange, publication leases and the pinned Pages data checkout. The golden allocator input is constructed from captured CSV/XML by `fixtures.golden()`, not a committed `allocator-golden.json`.

Current poll windows can be incomplete. The fixture's latest coherent window ends 18 July 2026. Keep missing Others observations missing; browser demonstrations use that explicitly labelled historical window, never substitute it for the current calculation.

M1 publishes theoretical seats: `occupied_house`, `vacancies` and definitive `majority` remain null when capacity is unchecked. Preserve this distinction. The 2023 assumption currently totals 71 electorate wins and says one unassigned electorate; retain that historical basis in published M1 data, but initialize the editable 2026 scenario with `71 - sum(wins)` unassigned and an explicit boundary-change label.

Replace these M1 restrictions deliberately:

- `build.py`, `verify.py` and `screenshots.py` hardcode six routes and prohibit scripts. Introduce validated route enumeration and allow only named local ES modules; retain static-content and injection checks.
- `export.py` hardcodes dataset fields, allowed files and date rules, and rejects all floats. Add explicit schemas, family ownership and a narrowly scoped GeoJSON coordinate exception. Poll and money arithmetic stays exact.
- `fixtures.captures()` loads every manifest entry; an absent unrelated capture must not break the official worked example or hourly polls. Add family-scoped loading with path, manifest and hash validation.
- `publish.py` owns only polls and copies `LICENCES.md` from the incoming bundle. Generalize per-family merging and regenerate shared operational files from the merged snapshot.
- `refresh.py` source collection includes every `ec-*` capture. Restrict historical seat provenance to actual dependencies, so adding 2026 captures cannot change the historical assumption's provenance.
- `source_note()` assumes Wikipedia source P. Add source-family rendering without relabelling EC, geography or market data as Wikipedia.

These are feature increments. Update obsolete M1-only assertions with stronger M2 contracts; do not remove regression coverage or alter tests merely to conceal defects.

## Capture contract and supervisor gates

All paths below are relative to `product/nz_election/fixtures/`. Each entry retains exactly the existing nine fields: `path`, `url`, `archive_url`, `captured_at`, `sha256`, `reviewer`, `revision`, `licence`, `notes`. Keep nullable fields explicit. Preserve raw bytes; record extraction methods for derived capture companions.

Use canonical UTC acquisition times. Put source observation dates, revision timestamps, archive dates, schema observations and extraction details in `notes`; parsers must verify dates against source content or a reviewed observation mapping. A rebuild never becomes a new acquisition.

Sizes below are expected ranges or estimates, not observed measurements unless stated. Record actual byte counts in capture review. Reject HTML challenges, truncated responses and ArcGIS transfer-limit responses even when HTTP status is 200.

Missing required acceptance captures fail the named capture test with `MISSING_CAPTURE: <path>`; hash mismatches retain `CAPTURE_HASH_MISMATCH: <path>`. Production refresh instead records the affected family unavailable or retains its dated last-good bundle. Render “Not available” with the reason; never publish zero or a successful empty dataset as a substitute.

### Before increment 4

No new capture required. Use the eleven existing captures, current configurations and synthetic scenarios held in tests. No Gamma capture exists in the inspected manifest, so markets are scheduled for increment 7.

### Before increment 5: geography and colour evidence

| File | Exact acquisition URL | Expected size and gate |
|---|---|---|
| `stats-nz/general-2025.geojson` | `https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/General_Electorates_2025/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&maxAllowableOffset=0.001` | Research: about 355 KB; 64 features; `test_required_boundary_captures` |
| `stats-nz/maori-2025.geojson` | `https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/M%C4%81ori_Electorates_2025/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&maxAllowableOffset=0.001` | Planning estimate 50-200 KB; measure seven features; same test |
| `stats-nz/general-2025-reference.json` | `https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/General_Electorates_2025/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson` | Compact reviewed reference, about 10-50 KB, derived once from approximately 21.3 MB upstream geometry; `test_reference_capture_required` |
| `stats-nz/maori-2025-reference.json` | `https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/M%C4%81ori_Electorates_2025/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson` | Compact reviewed reference, about 2-20 KB, derived once from approximately 4.6 MB upstream geometry; same test |
| `representation-commission/report-2025.html` | `https://elections.nz/democracy-in-nz/historical-events/boundary-review-2025/report-of-the-representation-commission-2025/` | Estimate 50-500 KB; supporting schedules may require separate manifest entries with their actual URLs; `test_correspondence_evidence` |

The reference companions contain per-feature IDs, component counts, extents, projected areas and representative interior points, with the full-response hash and derivation procedure in notes. The supervisor performs this one-time reference preparation; do not download or commit full-detail geometry routinely. Do not derive the reference from the simplified capture being tested.

`config/electorate-correspondence.json` is committed reviewed configuration, not a purported official concordance capture. The supervisor reviews all 2020-to-2025 relationships against the Commission report/schedules and official names. Each entry records old IDs/names, new stable IDs, relationship, explanatory note, evidence locator, reviewer and review date. No population weighting or vote reallocation.

Before M2 screenshot acceptance, capture official party identity evidence into `party-identity/{nat,lab,grn,act,nzf,tpm,opp}.html` from, respectively, `https://www.national.org.nz/`, `https://www.labour.org.nz/`, `https://www.greens.org.nz/`, `https://www.act.org.nz/`, `https://www.nzfirst.nz/`, `https://www.maoriparty.org.nz/` and `https://www.opportunity.org.nz/`. Estimate 20-500 KB each. Record actual redirects and any logo/CSS resource used as separately manifested evidence with its exact resolved URL; HTML without visible identity evidence is insufficient.

The supervisor records sampled colours, dated source locators and reviewer in `config/party-colours.json`. Do not redistribute logos. `test_party_colour_evidence` is an M2 acceptance gate; unverified additional parties use labelled neutral patterns. Increment 4 screenshots may be inspected provisionally using M1 colours, but do not constitute final M2 colour acceptance.

Without geography captures, retain the directory if its reviewed registry exists and show “Map not available”; no invented outlines. Missing correspondence leaves comparisons unresolved, rather than assuming unchanged boundaries.

### Before increment 6: candidates, baselines and enrolment

| File | Exact acquisition URL or expansion | Expected size and gate |
|---|---|---|
| Existing `ec-2023/party-votes.csv` | Origin `https://electionresults.govt.nz/electionresults_2023/statistics/csv/votes-for-registered-parties-by-electorate.csv`; captured raw URL `https://web.archive.org/web/20250218101127id_/https://electionresults.govt.nz/electionresults_2023/statistics/csv/votes-for-registered-parties-by-electorate.csv` | Existing capture, tens of KB; reuse all electorate rows; `test_required_baseline_captures` |
| `ec-2023/candidate-votes-by-voting-place-N.csv`, for every integer N from 1 through 72 | Origin `https://electionresults.govt.nz/electionresults_2023/statistics/csv/candidate-votes-by-voting-place-N.csv`; replace N with its unpadded decimal number | Research estimate about 10 KB each; same test |
| `ec-2026/electorate-candidates.xlsx` | `https://elections.nz/assets/pagecomponent-file-files/Electorate-Candidates-2026.xlsx` | Research: 31 KB, 469 rows; `test_required_candidate_captures` |
| `ec-2026/party-lists.pdf` | `https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf` | Research: 2.3 MB; same test |
| `ec-2026/enrolment-general.html` | `https://elections.nz/stats-and-research/enrolment-statistics/enrolment-by-general-electorate/?name=all` | Estimate 50-500 KB; `test_enrolment_capture_has_observation_date` |
| `ec-2026/enrolment-maori.html` | `https://elections.nz/stats-and-research/enrolment-statistics/enrolment-by-maori-electorate/?name=all` | Estimate 10-200 KB; same test |
| `wikipedia/candidates-2026.api.json` and `wikipedia/candidates-2026.wikitext` | Pinned API URL below; second file is verbatim main-slot content | Estimate 100-500 KB each; `test_candidates_revision_capture` |
| `wikidata/candidacies-2026.sparql.json` | Encoded query URL below | Estimate 0.2-2 MB; `test_wikidata_capture_and_mapping` |

Candidate-vote captures require Wayback raw bytes because the origin returns 403. For each N, discover the archive timestamp using `https://web.archive.org/cdx/search/cdx?url=electionresults.govt.nz%2Felectionresults_2023%2Fstatistics%2Fcsv%2Fcandidate-votes-by-voting-place-N.csv&output=json&filter=statuscode%3A200&fl=timestamp%2Coriginal&collapse=digest`. Then capture `https://web.archive.org/web/TIMESTAMPid_/https://electionresults.govt.nz/electionresults_2023/statistics/csv/candidate-votes-by-voting-place-N.csv`.

TIMESTAMP is the actual resolved archive timestamp, not a supplied or guessed value. Before dispatch, the manifest must enumerate all 72 concrete `id_` URLs. Check snapshot consistency and Port Waikato separately; do not incorporate its later by-election into the pre-Port Waikato general-election baseline.

Discover the candidate revision with `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Candidates_in_the_2026_New_Zealand_general_election_by_electorate&rvprop=ids%7Ctimestamp&format=json&formatversion=2&maxlag=5`. Capture using `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&revids=REVISION_ID&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main&format=json&formatversion=2&maxlag=5`. Replace REVISION_ID with the returned integer and commit that concrete URL, oldid link and contributor-history link. No candidate revision ID is established by the current repository.

Capture Wikidata using this exact query URL:
`https://query.wikidata.org/sparql?query=SELECT%20%3Fperson%20%3Fstatement%20%3Fparty%20%3Felectorate%20%3Frank%20WHERE%20%7B%20%3Fperson%20p%3AP3602%20%3Fstatement%20.%20%3Fstatement%20ps%3AP3602%20wd%3AQ104843407%20.%20OPTIONAL%20%7B%20%3Fstatement%20pq%3AP102%20%3Fparty%20%7D%20OPTIONAL%20%7B%20%3Fstatement%20pq%3AP768%20%3Felectorate%20%7D%20OPTIONAL%20%7B%20%3Fstatement%20pq%3AP1545%20%3Frank%20%7D%20%7D&format=json`.
Preserve statement URIs and acquisition time; the research's 530 people and 912 statements are diagnostics, not required equality.

Read XLSX through bounded `zipfile`/ElementTree parsing of workbook relationships, shared strings and cells. Do not implement a general PDF parser. The supervisor transcribes and reviews the party-list PDF into `config/ec-party-lists-2026.json`, recording PDF hash, page/column/rank locators and review details. List capacity remains unchecked until completeness and identities are reviewed.

If enrolment responses are shells, retain them as evidence of unavailable data, not numeric observations. If dates or tables are absent, the acceptance test fails and the UI says unavailable. Older verified observations may ship with their actual dates.

Missing EC candidates means official candidates unavailable; missing supplemental captures means Wikipedia/Wikidata fields unavailable. Missing candidate votes means no candidate baseline. Missing mappings means “Unresolved”, never surname matching.

### Before increment 7: Gamma events

Capture one JSON file per explicitly named research slug, using the full URL in the second column. Record observation time as capture time, distinct from any upstream update timestamp.

| File | Exact URL |
|---|---|
| `polymarket/next-prime-minister-of-new-zealand-174.json` | `https://gamma-api.polymarket.com/events?slug=next-prime-minister-of-new-zealand-174` |
| `polymarket/which-parties-will-be-part-of-the-next-government-of-new-zealand.json` | `https://gamma-api.polymarket.com/events?slug=which-parties-will-be-part-of-the-next-government-of-new-zealand` |
| `polymarket/nz-election-national-party-of-seats.json` | `https://gamma-api.polymarket.com/events?slug=nz-election-national-party-of-seats` |
| `polymarket/nz-election-labour-party-of-seats.json` | `https://gamma-api.polymarket.com/events?slug=nz-election-labour-party-of-seats` |
| `polymarket/new-zealand-election-turnout.json` | `https://gamma-api.polymarket.com/events?slug=new-zealand-election-turnout` |

Estimate 10-300 KB per event; review actual size and outcome count. `test_required_gamma_captures` fails on absence, wrong slug or empty event response. Research's ellipsis is not an additional allowlist. Turnout is captured but explicitly excluded from the three M2 displayed contract families, with a recorded exclusion reason.

Use the manifest licence text “Source: Polymarket. Subject to Polymarket terms. No open licence asserted.” Preserve resolution wording in normalized metadata and a link to the individual market's rules. Missing captures produce an unavailable panel; stale last-good prices retain their original observation time.

## Data contracts and family boundaries

Retain `schema_version=1`, `source`, `fetched_at`, `run_url`, `code_sha`, `data`; derived outputs additionally carry `input_hashes`, `method_version`, `generated_at`. Source entries retain `id,url,revision,licence,fetched_at,history_url`. All rows have `id,source_ref,observed_at`; field-level references point to source IDs and source row/page/statement locators.

Extend schema validation explicitly for date-only baseline/enrolment observations and instant observations. Never globally relax canonical timestamp validation. Every dataset has a CSV sibling; nested structures use documented canonical JSON columns. Downloads enumerate all files with hashes, sizes, licences, dates and immutable data-commit links.

| Dataset | Payload beyond common row fields |
|---|---|
| `electorates.json` | `name,kind,slug,stats_id,search_key,baseline_ids,boundary_note,mapping_status` |
| `candidates.json` | `person_id,name,party_id,electorate_id,list_rank,wikidata_id,wikipedia_url,join_status,conflict_ids,field_sources` |
| `party-lists.json` | `party_id,candidate_ids,complete,review_ref,field_sources`; ordered IDs refer to people, including list-only candidates |
| `candidate-review.json` | `person_id,electorate_id,field,claims,resolution,review_ref`; unresolved claims retain all conflicting values and provenance |
| `baseline-2023.json` | `old_electorate_id,old_name,election_date,result_as_of,party_votes,candidate_votes,field_sources`; nested votes include source IDs/names, integer votes and references |
| `enrolment.json` | `electorate_id,as_of,enrolled,eligible,roll_basis,field_sources`; unknown values are null, not zero |
| `electorate-polls.json` | `electorate_id,poll_id,pollster,fieldwork_start,fieldwork_end,sample,measure,shares,scale,reference_urls,boundary_basis` |
| `markets.json` | `event_id,event_slug,market_id,family,question,outcomes,volume,volume_unit,liquidity,liquidity_unit,resolution_url,resolution_criteria,updated_at`; outcomes contain IDs/names and exact decimal price strings |

Candidate row IDs identify candidacies; `person_id` identifies the reviewed person. List-only records have null electorate IDs. Do not equate rows, people, lists and candidacies.

Boundary files are valid GeoJSON FeatureCollections with common envelope metadata as foreign members, `features` as geometry payload and `data` as metadata rows keyed to the same feature IDs. Features retain official properties and stable IDs. A boundary-specific validator and CSV adapter prevent duplicate or mismatched IDs; CSV rows include metadata plus `geometry_json`. Permit finite numeric coordinates only within geometry, keeping other dataset arithmetic exact.

Group atomic outputs as `geography` (both boundaries and electorate registry), `candidates` (candidates, party lists, review), `baseline-2023`, `enrolment`, `electorate-polls`, and `markets`. Each group validates and advances independently; dependencies must match reviewed registry/config hashes. Existing hourly polls remain their own atomic family.

## Coalition explorer

Add `pipeline/coalitions.py`, `web/coalitions.mjs` and a small Node runner. The ES module imports the existing allocator and reads only same-origin published `averages.json` and `seats.json`, plus reviewed candidate/list exports when available. Validate matching average IDs and snapshot inputs before enabling controls.

Render static calculated seats and provenance first. Initially select no parties. Label controls “Choose parties” and “Electorate seats assumed”; restrict wins to whole non-negative counts with a total at most 71, show unassigned seats, and enforce known candidate capacity. Others is never selectable or eligible for seats.

Before candidate capacity exists, use `entitlement()` with the explicit sufficient-list assumption; keep actual occupied House and vacancies unknown. Show “Seats needed for a majority” with the conditional assumed House. Do not create imaginary list candidates to call `allocate()`.

With complete reviewed candidate/list data, allow explicit hypothetical winner selection using actual candidate IDs. Count edits require consistent winner selections before claiming checked capacity; counts alone do not establish which list candidates must be skipped. Non-list winners are explicit actual IDs and reduce proportional seats. Checked scenarios call `allocate()`, retain overhang, skip elected list candidates and leave exhausted-list vacancies unfilled.

Calculate majority as `floor(occupied_house / 2) + 1`; selected coalition total sums occupied party seats. Report seats short or above the majority line without saying a government will form. Suppress definitive totals on unresolved ties, incomplete averages or inconsistent inputs.

Store versioned state in `#coalition=<percent-encoded JSON>`: selected party IDs, electorate counts, optional winner IDs/non-list IDs, mode and input fingerprint. Default selection is empty; Reset restores it. Preserve state on reload and hash navigation. Warn when linked inputs differ from the current snapshot. Reject oversized hashes, unknown keys/IDs and invalid values; use textContent, never source HTML.

Use a shared scenario validator in Python and JS with `INVALID_COALITION_STATE` for malformed state. Probe empty, null, wrong type, fractional, huge, Unicode, prototype-like and duplicate values. Bound hash length and integer length before conversion; do not expose the deferred allocator huge-string defect through this interface.

Without JS, controls remain hidden or inert with an explanatory note; static data remains readable. Load controls only after valid inputs arrive. A failed module or data request does not remove static content. Use the existing strip proportions, white count labels, anchored mobile lanes, majority marker and a polite live region announcing selected seats and the majority requirement.

`verify.py coalitions` compares Python/JS scenarios including the official golden, multiple overhangs, exhausted lists, unknown capacity and unresolved ties; prints `PASS coalitions`. Host browser script `tests/coalitions_browser.py`, function `test_coalition_edits_hash_and_nojs`, verifies keyboard selection, count edits, vacancy/majority changes, hash reload/back, invalid state and JS-disabled fallback; prints `PASS coalition browser`.

## Geography and directory

Add `pipeline/geography.py`, `web/electorates.mjs`, `web/templates/electorates.html` and committed `config/electorates.json`. Registry IDs use a namespace plus the official 2025 Stats NZ code, not array position or future EC feed IDs. Store exact macron names, general/Māori kind, stable ASCII slugs and normalized search keys. Slugs remain stable if display names change.

Validate exactly 64 general and seven Māori IDs against the reviewed registry. Reject duplicate IDs, unsupported geometry, empty polygons, unclosed rings, too-short rings, non-finite coordinates and coordinates outside WGS84. Preserve holes and island components.

Use a documented spherical Lambert cylindrical equal-area projection centered at longitude 173°, standard parallel -41°. Unwrap longitude consistently about that meridian before projection; keep antimeridian islands near NZ rather than drawing world-spanning edges. Use the same projection for reference area comparisons.

Compare capture/output IDs, component counts, extents and representative interior points with committed reference summaries. Aggregate projected area change must be at most 1% per layer; investigate failures rather than increasing tolerance.

Generate SVG at build time with a computed padded `viewBox`, one labelled linked feature path per electorate, even-odd hole filling, escaped `<title>` names and an accessible description/source link. No tiles, runtime geometry library or browser GeoJSON conversion. Detail pages receive only their own outline.

Render the entire directory without JS, grouped into general and Māori sections. At increment 5 map links target existing directory anchors; increment 6 changes them to detail routes. The small module enhances search using Unicode decomposition/macron removal, case folding and whitespace normalization; no-JS retains the full list. General/Māori selectors keep a readable fallback.

Selection uses a strong outline/pattern and a named summary, not party-colour inference. Provide 3px blue focus with white separation. Small geographical shapes cannot guarantee 44px targets: provide adjacent 44px directory links and selection controls as the equivalent interaction, and avoid forcing keyboard users through 71 paths.

Budgets use uncompressed UTF-8 bytes: simplified general capture below 500,000; Māori capture initially at most 200,000; combined inline map SVG at most 300,000 per index page; detail outline at most 30,000. Measure Māori bytes before dispatch and record the measured budget in config; if the proposed ceiling fails, review simplification while preserving the 1% test rather than silently raising it.

`test_svg_page_budget` measures all inline and linked SVG bytes required by a page, including both layers, not just HTML length or gzip size. Geometry remains a download, not duplicated as embedded JSON. `verify.py geography` prints `PASS geography: 64 general, 7 Māori`.

## Candidates, baselines and electorate pages

Add `pipeline/{candidates,baseline,enrolment,electorate_polls}.py`, reviewed `config/{candidate-mappings,candidate-review,electorate-aliases}.json` and `web/templates/electorate.html`.

EC official names and party affiliation form the spine. Bind spreadsheet rows, list ranks and electorate aliases through explicit reviewed identifiers. Wikipedia page/section/box locators and Wikidata statement IDs attach through mappings containing electorate, party, rank where available, evidence and reviewer. Never join by surname, fuzzy similarity or source row-count equality.

Preserve conflicting names, ranks and identities in `candidate-review.json`; show “Unresolved” beside affected fields. EC remains authoritative for official name/party. Missing supplemental claims are unavailable, not disagreements. Do not fabricate Wikidata IDs or inferred list ranks.

Render 71 detail pages at `/unattended/nz-election/electorates/<slug>/` from one template. Each shows the electorate name and selected outline; official candidates and field-level sources; separately labelled original-electorate 2023 party and candidate tables; reviewed successor/boundary notes; enrolment with its actual observation date and roll basis; and local polls where captured.

Parse existing party-vote CSV electorate rows, excluding national totals from aggregation. For candidate-vote files, use the explicit electorate total rows after reviewing their schema; never sum totals and voting-place rows together. Preserve Port Waikato's absence/deferred contest distinctly from zero votes.

A successor can show several separately named old-electorate comparisons. Never sum them into a purported 2025 result. Missing correspondence shows unresolved comparison. Local poll mapping preserves old/new boundary basis and separates candidate vote, party vote and other measures.

Extract local polls from the already committed polling wikitext through a separate parser; retain the national parser's exclusions. An empty result is valid only when diagnostics prove there are no relevant rows; an unsupported captured local table fails `parse_drift`. Daily ownership avoids racing the hourly national bundle and clearly labels the capture's age.

`verify.py candidates` prints `PASS candidates: 71 electorates`; it checks page coverage independently of candidate-row count. `verify.py electorates` prints `PASS electorates: 71 pages` and proves changed-boundary, missing-data and old-name displays.

## Markets

Add `pipeline/markets.py` and reviewed `config/markets.json` mapping explicit event slugs to contract families. Parse Gamma event arrays and JSON-encoded outcome/price arrays defensively; validate IDs, lengths, decimal ranges 0 through 1, finite amounts, units and links. Escape question/resolution text and permit only safe HTTP(S) source URLs.

Keep next-PM, government-membership and seat-band tables separate. Display “Market price” as price multiplied by 100, with display-only rounding. Show event wording, outcome, liquidity or volume with its documented unit, resolution criteria link and observation time. Never infer currency from a bare numeric field; record the reviewed Gamma unit evidence, or label the unit unavailable.

Do not normalize outcomes, treat membership contracts as mutually exclusive, turn prices into party-vote shares or feed them into allocation. Preserve closed/resolved status where relevant in question metadata or explicit display labels.

Place markets after coalition controls on mobile and beside supporting poll material on desktop, below the seat answer. Render the tables statically. Show the exact line “Source: Polymarket. Subject to Polymarket terms. No open licence asserted.” Link Polymarket and its terms; keep observation time beside prices. Publish normalized rows only.

`verify.py markets` checks all three displayed families, prices, units, criteria URLs, observation times and unavailable/stale states; prints `PASS markets`.

## Daily refresh, publication and Pages

Introduce `pipeline/daily_refresh.py` in increment 5 for offline processing, extending its families in increments 6 and 7. CLI: `uv run product/nz_election/pipeline/daily_refresh.py --out artifacts/nz-election/data`. It never fetches and labels local runs offline verification. Successful completion prints `PASS refresh: daily bundles`.

Create workflow `NZ election daily`, cron `'43 15 * * *'`, plus `workflow_dispatch`, main-only. Use the triggering code SHA and record the Action URL. Steps mirror hourly: checkout code with persisted credentials disabled; set up uv; resolve and checkout exact previous data SHA separately; process committed captures serially into staging; validate; upload only when `validated=true`; publish in a separate job with contents-write permission.

Handled family failures retain their bytes and publish status before the workflow reports failure. Unexpected exceptions block upload. Never treat filesystem errors or programmer exceptions as source absence.

Extend publication with an explicit `--family hourly|daily`, defaulting to hourly for compatibility. Hourly owns polls/averages/seats JSON/CSV; daily owns only the M2 geography, candidate, baseline, enrolment, local-poll and markets JSON/CSV sets. Reject undeclared paths and invalid family selection before git or credential access.

Both publication jobs use `nz-election-data-publication`, `cancel-in-progress: false`. Retain the existing three-attempt lease algorithm: reread tip, validate tree, merge owned families onto fetched parent, push with the exact expected ref, and retry only when the remote ref moved. Test simultaneous bootstrap and hourly/daily races in local bare repositories.

Compare freshness per family, not by polls' timestamp or the maximum timestamp of mixed sources. Compare matching source-acquisition vectors; reject any source regression or incompatible mixed generations. For identical acquisitions, use successful `generated_at`; exact ties retain current bytes. Merge last-attempt chronology independently from last-good data.

Regenerate `status.json/.csv`, `manifest.json/.csv` and `LICENCES.md` from the merged union. Neither writer may overwrite another family's licences, status or files. Preserve original successful run/code provenance for retained bytes.

Keep existing status fields: `dataset,state,last_attempt_at,last_success_at,last_good_run_url,error_code,message` plus common row fields. Add entries for each daily atomic family. Daily `last_success_at` means successful ingestion time; acquisition remains in source metadata. A successful unchanged capture is a successful run, not a fresh observation. Show daily overdue after 36 hours, source observation age separately, and unavailable when no validated bundle exists.

Add `NZ election daily` to `pages.yml`'s completed `workflow_run` list. Preserve same-repository/main guards, completion regardless of conclusion, non-cancelling `pages` concurrency, rollback validation, exact data checkout, actual SHA recording and product-before-blog ordering. No data-tree code executes. Do not rely on GITHUB_TOKEN pushes to trigger Pages.

## Design and accessibility

Apply the frontend-design skill while preserving the accepted ballot-paper direction. Keep Arial/Helvetica Neue/system sans because fonts cannot be downloaded and familiar ballot labels suit the task. Use tabular numerals, 14/16/20/28/40px scale, white paper, ink `#181818`, muted `#595959`, surface `#F0F2F4`, orange `#F58220` and focus blue `#005EA8`.

Use 16px phone and 32px desktop gutters, 1120px maximum width and the existing 800px breakpoint. Counts stay inside figures with white inset labels or anchored lanes. Orange uses dark text and an ink boundary. No meaning depends on colour, hover or dragging.

The seat strip, country silhouette and selected outline are the respective visual priorities. Supporting controls and tables remain quiet. Use voter copy such as “Seats needed for a majority”, “Last poll ended…” and “Enrolment at…”. Link calculation inputs and named source organisations; do not present “this project” as the authority.

Controls and directory links have 44px targets; all keyboard focus is visible. Check text contrast at 4.5:1 and meaningful boundaries at 3:1, including SVG selection and focus. Respect reduced motion. Local table scrolling must not create page-wide overflow at 390px. Preserve static tables, source notes and downloads with JS disabled.

## Verification and test inventory

New test files and principal functions:

| File | Functions and coverage |
|---|---|
| `test_coalitions.py` | `test_no_preselected_coalition`, `test_scenario_python_js_parity`, `test_overhang_and_list_vacancies`, `test_unknown_capacity_stays_conditional`, `test_invalid_state_error_parity`, `test_incomplete_average_disables_explorer` |
| `test_geojson.py` | `test_required_boundary_captures`, `test_reference_capture_required`, `test_64_general_7_maori_ids`, `test_closed_finite_wgs84_rings`, `test_antimeridian_projection`, `test_reference_components_extents_and_area` |
| `test_geography.py` | `test_slug_registry_and_macron_search`, `test_correspondence_evidence`, `test_svg_links_titles_and_holes`, `test_svg_page_budget`, `test_missing_geometry_is_unavailable`, `test_party_colour_evidence` |
| `test_candidates.py` | `test_required_candidate_captures`, `test_candidates_revision_capture`, `test_wikidata_capture_and_mapping`, `test_official_spine_and_explicit_joins`, `test_conflicts_preserved`, `test_list_capacity_requires_complete_review` |
| `test_electorates.py` | `test_required_baseline_captures`, `test_original_names_and_successor_comparisons`, `test_no_total_double_count`, `test_port_waikato_not_fabricated`, `test_enrolment_capture_has_observation_date`, `test_local_poll_measures_separate`, `test_71_pages_and_missing_data` |
| `test_markets.py` | `test_required_gamma_captures`, `test_three_contract_families`, `test_exact_prices_units_and_resolution`, `test_missing_market_capture_unavailable`, `test_market_terms_and_observation_rendered` |
| `test_daily_pipeline.py` | `test_family_scoped_capture_failure`, `test_partial_daily_failure_retains_family`, `test_daily_first_failure_status`, `test_hourly_daily_race_preserves_union`, `test_daily_mixed_source_regression_rejected`, `test_shared_licences_and_inventory_union`, `test_daily_overdue_after_36_hours` |
| `test_m2_contracts.py` | `test_geometry_only_decimal_exception`, `test_m2_csv_roundtrip_and_manifest`, `test_source_family_rendering`, `test_m2_dates_and_instants`, `test_capture_paths_and_unknown_files_rejected` |
| `test_daily_workflows.py` | `test_daily_schedule_and_dispatch`, `test_daily_never_fetches`, `test_shared_publication_concurrency`, `test_pages_daily_completion_guard`, `test_failure_status_published_before_exit` |

Add parser malformed-input matrices, unsafe URL/path cases and candidate conflict fixtures as synthetic test data outside immutable captures. Keep Node parity mandatory. Preserve pytest collection of both root and product suites.

Extend the verifier registry incrementally with coalitions, geography, candidates, electorates and markets. At M2, `verify.py all` prints existing polls/thresholds/provenance/pipeline lines, the five new lines, then `PASS all`. Provenance verifies every M2 JSON/CSV and field source; pipeline verifies independent-family retention and concurrent publication. Optional `--data` and `--site` must inspect the supplied artifacts, not merely run fixture checks.

Retain six primary navigation routes. Generate 71 detail routes from the registry, yielding 77 routes without a separate map route. The map is on the electorates index; do not count it twice. Required named visual coverage includes the six existing routes, a reviewed changed-boundary detail such as Wellington North, and a Māori detail with a controlled missing-data state, such as Te Tai Tonga. Final baseline capture covers all 77, exceeding the eight-route minimum.

Host-run command, using installed Playwright/Chromium:
`uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
Expected after increment 6: `PASS screenshots: 77 routes, 154 baseline images`. Increment 4/5 remain six routes and 12 baseline images. Encode nested route names safely in filenames.

Keep M1's eight additional state images; add both map layers, selected-map focus, coalition edit, coalition vacancy and electorate missing-data states at both sizes: 12 further images, 20 additional state images total. Record these separately from baseline counts. Inspect actual images at 390x844 and 1280x800.

Host-run coalition command:
`uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site site`
Expected `PASS coalition browser`. Browser checks block non-loopback requests. Replace whole-main JS/no-JS text equality with equality of identified static data sections, while asserting controls are absent/inert without JS. Check local module requests, console errors, prefix safety, broken links, keyboard operation, focus, contrast and reduced motion.

## Build order

- [ ] **Increment 4, PR: coalition explorer only.** No new captures. Add scenario modules, static enhancement, hash state, verifier and browser test; preserve conditional capacity. Target about 12 new deterministic cases, not a gate. Prove `uv run product/nz_election/pipeline/verify.py coalitions` prints `PASS coalitions`; run host coalition browser and six-route screenshots, inspecting 12 baseline images. Close with `bin/lint` and `uv run --with pytest pytest -q`.
- [x] **Increment 5, PR: geography and directory.** (merged 3f95c7a, PR #13, 2026-10-16T19:47Z) Supervisor supplies geography/reference captures, reviewed registry/correspondence and colour evidence. Add family-aware export/publication foundations, offline daily refresh, SVG generator, directory/search and geography tests. Keep map links to directory anchors until details ship. Target about 24 additional deterministic cases. Prove `uv run product/nz_election/pipeline/verify.py geography` prints `PASS geography: 64 general, 7 Māori`; run `test_geojson.py`, six-route host screenshots and both map states. Close with `bin/lint` and `uv run --with pytest pytest -q`.
- [ ] **Increment 6, PR: candidates, baselines and 71 pages.** Supervisor supplies candidate/baseline/enrolment/supplemental captures and reviewed joins. Extend daily processing, generate all details, connect map links and add capacity-aware explorer mode where evidence is complete. Target about 28 additional deterministic cases. Prove `verify.py candidates` prints `PASS candidates: 71 electorates` and `verify.py electorates` prints `PASS electorates: 71 pages`, using the full `uv run product/nz_election/pipeline/verify.py` command prefix. Inspect host screenshots: `PASS screenshots: 77 routes, 154 baseline images`. Close with `bin/lint` and `uv run --with pytest pytest -q`.
- [ ] **Increment 7, PR: markets and daily automation.** Supervisor supplies Gamma captures. Add normalized markets, static panel, daily workflow, Pages trigger and operational runbook. Target about 22 additional deterministic cases. Prove `uv run product/nz_election/pipeline/verify.py markets` prints `PASS markets`, and `uv run product/nz_election/pipeline/verify.py all` ends `PASS all`. Run host coalition browser and all screenshots again. Close with `bin/lint` and `uv run --with pytest pytest -q`.
- [x] **M2 deployment acceptance, supervisor.** Dispatch daily after merge, verify the data-branch union beside hourly polls, subsequent Pages completion, actual code/data SHAs, downloaded manifests and deployed map/explorer/market views. Record Action URLs and durations. Verify an hourly run after daily retains all daily files. M2 closes only after deployment and accepted screenshots. Accepted 2026-10-24T18:05Z (25 Oct NZ): daily success 20 to 23 Oct (runs 39484613874, 39663178648, 39840576223, 40012162765), hourly success with daily files retained (40110212811, 40103199866), Pages success 40117790231, seven routes 200 live, home screenshots at 390 and 1280 of the live site looked at and accepted (nits: "Change since 2026-10-24" ISO date beside "24 Oct 2026" prose).

For each PR, stage intended new files before lint; preserve `lint ok (<N> text files)`. Quote actual full-suite output and explain departures from test-count targets. Run the relevant verifier plus `verify.py all` for checks implemented so far. Missing tools/captures fail explicitly, never skip. Review in `REVIEW.md` order: bugs, security, compliance.

For reproducible screenshots, prepare offline poll output with the existing `refresh.py --fixtures --out artifacts/nz-election/data`, add daily outputs using `daily_refresh.py`, then build with `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`. Expected build line is `PASS build: 6 routes` through increment 5 and `PASS build: 77 routes` thereafter. Synthetic and historical demonstration states must remain visibly labelled.

## Concerns

- Exact candidate revision, new archive timestamps, Māori simplified size and official identity resources are not established by committed evidence. This plan gives acquisition URLs and deterministic discovery rules; the supervisor must commit concrete resolved records before dependent dispatch. Do not invent pins or claim the endpoints were checked in this planning run.
- Research row counts disagree because they describe different populations. Preserve people, candidacies and list memberships separately; reviewed mappings, not expected counts, determine identity.
- Full s193 output needs actual list identities and hypothetical winner identities. Count-only editing remains explicitly conditional. Missing capacity evidence cannot justify a definitive occupied House.
- The spec table assigns markets/local polls hourly; this brief requires committed daily ingestion. M2 intentionally assigns both to daily ownership, labels capture observations and does not add Gamma HTTP fetching.
- Geometry requires JSON decimals while M1 prohibits floats globally. The exception is confined to validated coordinate arrays and guarded by `test_geometry_only_decimal_exception`; market prices remain decimal strings.
- Candidate baselines need 72 old-electorate source files while the UI has 71 current pages. Port Waikato and changed boundaries need explicit notes, not forced count matching or re-cut totals.
- Seventy-one pages must not each embed the national map. Budget the index SVG at 300 KB and detail outlines at 30 KB each; total outline ceiling is about 2.43 MB before HTML/data. Record actual total site bytes and largest pages. Shared downloads are copied once.
- Pages now renders 77 pages and validates more families on every hourly deployment. Cache parsed captures within a process, avoid recomputing the golden for every page, and measure build/verify durations separately. Compare actual durations over several days; retain cadence unless the supervisor records a change.
- M1 publication, schema validation, capture loading, route checks and source rendering require structural changes, guarded respectively by race/union, geometry/CSV, scoped-capture, 71-page and source-family tests. Preserve exact timestamp ordering, directory-exchange safety, rollback and existing malformed-input regressions.
- An old M1 code rollback cannot understand M2 data filenames. Runbook rollback must select a compatible code/data SHA pair; never weaken the unknown-file allowlist for backward compatibility.
- No runtime code can guarantee a daily source was newly observed. Distinguish successful ingestion, acquisition age and source observation date. Missing required captures block acceptance, while deployed pages retain honest dated or unavailable states.
## Supervisor decisions (2026-10-17 NZ, accepted)

Plan job `plan-nz-election-m2` (read-only, 380 s). Accepted as written except where a decision below says otherwise. Decisions override the body.

1. **Increment 4 needs no capture.** Confirmed against `fixtures/manifest.json` (11 entries, none geographic or market). Dispatched first, in `.worktrees/nz-election-4`.
2. **Geometry reference companions are produced by a product tool, not by hand.** Increment 5 delivers `pipeline/geo_reference.py` (stdlib, reads a full-detail FeatureCollection from a path outside the repo, writes the compact reference with IDs, component counts, extents, projected areas and interior points, and prints the input sha256). The supervisor downloads the full-detail responses to a gitignored path, runs the tool on the host, commits the two reference files and the two simplified captures on the change branch before the fresh review, and records the full-response hashes in the manifest notes. `test_reference_capture_required` therefore passes on the host run, not in the sandbox; the brief says so.
3. **Party identity evidence is one HTML capture per party.** Seven HTML files as the plan lists. A stylesheet is captured only when the HTML carries no colour value; logo files are never captured. `config/party-colours.json` records the sampled value, the capture path and a locator (CSS selector or element). Increment 4 screenshots use M1 colours; final colour acceptance is at increment 5.
4. **Correspondence config is reviewed by the supervisor** from the Representation Commission report capture; each entry carries the evidence locator and the review date. No population weighting. Missing entries render unresolved.
5. **Daily workflow fetches live what the hourly already proves fetchable, and ingests captures for the rest.** Departure from the body: `nz-election-daily.yml` acquires the Wikipedia candidates page (same API host, same fetch.py transport, pinned revision recorded) and the five Gamma events (second allowed host, same bounded transport, response cap, retries) in increment 7. ArcGIS geometry, EC files and the Representation Commission report stay committed captures because they are bot-walled or static for the campaign. Committed captures remain the offline test inputs for every family. Spec requirement 5's hourly cadence for markets is amended to daily: markets are a dated panel, not a feed.
6. **Race and ownership.** Daily at 15:43 UTC, hourly at 17 past the hour, both under the `nz-election-data-publication` concurrency group with the existing lease algorithm and disjoint owned file sets. `status.json`, `manifest.json` and `LICENCES.md` are regenerated from the merged union by whichever writer runs; `test_hourly_daily_race_preserves_union` is the gate. 36-hour overdue for daily families stands.
7. **Byte budgets stand** (general capture under 500,000; Māori at most 200,000 subject to measurement before increment 5 dispatch; index SVG at most 300,000; detail outline at most 30,000), measured in uncompressed UTF-8 bytes by `test_svg_page_budget`. The supervisor records the measured Māori size in the increment 5 brief.
8. **Test counts are targets, PASS lines are contracts.** As in the M1 plan. The five new verifier lines, `PASS build: 77 routes` and `PASS screenshots: 77 routes, 154 baseline images` are the acceptance strings.
9. **Markets stay out of allocation**, prices are decimal strings, display is price times 100 with display-only rounding. Turnout captured, excluded from display with the recorded reason.
10. **Design stands** (ballot-paper direction, tokens, counts inside figures, voter copy, no meaning by colour alone). The coalition explorer starts with no parties selected. Each UI increment's definition of done includes phone and desktop screenshots that the supervisor inspects and the fresh review judges.

## Increment 6 implementation notes

- The 469 EC electorate rows and 443 transcribed list records retain separate source identities;
  `person_id` is null pending identity review. No list record is inferred to be an electorate
  candidate. All 71 EC electorate strings have exact NFC registry matches.
- Exact NFC triple proposals currently number zero. Wikipedia displays names in a different
  form; the Wikidata statement capture has no name labels. No name reordering or party alias
  inference is used to manufacture proposals. The generated proposal is outside config and is
  never a build input.
- The enrolment captures are national age tables, dated 30 September 2024 (general) and
  31 August 2024 (Māori). Electorate totals and eligible counts stay null. Pages disclose the
  national roll basis and actual date; no national figure is assigned to an electorate.
- Local polling has 27 measure rows. The Kāpiti and Mount Albert source headings have no exact
  registry name match (Kapiti and Mt Albert). Their rows remain in downloads with unresolved
  mappings. The month-only Kāpiti observation retains its original label and null day bounds;
  its acquisition instant is explicitly separate from fieldwork. Approximate shares retain
  an approximation flag. These are conservative departures from complete mapped local tables.
- Māngere's missing candidate-vote capture leaves that baseline null and the required-capture
  test failing. Port Waikato's cancelled general-election contest also has a null candidate
  baseline, with a distinct reason. No later by-election is substituted.
- Host screenshot inspection remains required: local Chromium launch fails at the sandbox's
  Mach port permission boundary. The script covers 77 routes, safe nested filenames, changed
  boundaries and controlled missing data, with 20 additional state images.
- Offline build measurement: 14,736,580 total site bytes including shared downloads; largest
  HTML pages are the directory (307,072 bytes), downloads (178,510 bytes), and West Coast-Tasman
  (53,793 bytes). Index SVG is 286,091 bytes; largest single outline is 15,364 bytes. A static
  crawl checked 1,310 local links. These measurements are not browser layout acceptance.
- Final deterministic suite: 336 passed, one failed (required Māngere capture). The anticipated
  geography reference absence did not occur: both reference companions are present and its
  gate passes. All eight implemented verifier checks pass, ending `PASS all`.

## Increment 7 implementation notes

- Decision 5 overrides the offline-only workflow wording: `--live` acquires Wikipedia
  candidates and all five Gamma events through the bounded transport. The default daily CLI
  remains offline. Expected live failures fall back to the committed family with original
  observation times and an explicit status message. Reviewed candidate claims cannot be
  relabelled with changed Wikipedia content; that case requires review and uses the capture.
- The next-PM capture has 27 inactive contracts without an `outcomePrices` key. They remain
  normalized rows with `unpriced_outcomes` (IDs and names), empty priced `outcomes`, and an
  explicit unavailable display. No null, float or invented zero is accepted as a price.
  All 54 non-turnout contracts remain present. Turnout is validated but excluded from display.
- The home markets module follows the polls module, as the later home plan requires. Existing
  CSS and accessible table/source shapes are reused; there is no additional route.
- The exact Pages workflow-list assertion must gain the daily trigger to test the authorized
  trigger change. No other existing workflow assertion changes. Manifest count becomes 116;
  the existing dynamic ownership/race assertions automatically gain the markets family.
- Operational instructions are added at the brief's named `runbook/nz-election.md`; existing
  M1 and social instructions remain in `product/nz_election/runbook.md`.


## Increment 7 fix round 1

- The supervisor's PR #30 fix brief supersedes the earlier capture-fallback and unavailable-unit
  policies. Live acquisition or validation failures now propagate to last-good retention and
  non-zero workflow completion. First-run failures publish unavailable status without fixtures.
- The supervisor instructs USD for Gamma volume and liquidity. Config records that authority,
  not an invented documentation capture. New normalized rows carry USD; retained legacy null
  units remain readable under this reviewed source-level USD interpretation. Display rounds
  to whole USD; published values and allocation arithmetic remain unchanged.
- The home shows one highest priced Yes contract per event: next PM, government membership,
  National seat band and Labour seat band. Membership prices remain independent, and the
  selected band is not a seat projection. Ties use stable market IDs. No full-list HTML route
  is published; normalized downloads retain all evidence. Empty events get one line.
- Unpriced contracts and placeholder questions/outcomes are excluded before ranking. There
  are at most four home rows, one rules link per event and one optional amounts disclosure.
- The screenshot harness adds an 844 px maximum at 390 px width and checks all pages for
  excluded contracts. Existing main-branch checks and the 219-image inventory remain intact;
  market closeups and bounding-box JSON are additional outputs outside that baseline inventory.
