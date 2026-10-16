# Data inventory for a 2026 NZ general election web app (2026-10-16)

Produced by the supervising session's research agent after Byron's steer (issue #7). Status key: C = fetched and inspected, I = inferred. Read the access table first: most Electoral Commission and Parliament HTML is behind bot walls, so the pipeline design follows from what is scriptable. Scratch files the agent left under /tmp are not part of the repo.

Status key: **C** = fetched and inspected in this session, **I** = inferred from search results, archives or 2023 precedent. Fact corrections to the brief: there are **71 electorates (64 general + 7 Maori)**, not 72; nominations closed noon Thu 8 Oct 2026, lists published 9 Oct.

## Access reality (read first)

| Host | Bot wall | Scriptable from GitHub Actions? | Status |
|---|---|---|---|
| elections.nz, vote.nz | Imperva Incapsula; blocks curl, WebFetch and headless Chromium | No. Use Wayback (`web.archive.org/web/<ts>id_/<url>`, CDX API) or fetch once by hand and commit | C |
| electionresults.govt.nz `/`, `/electionresults_YYYY/`, `/statistics/**` | Cloudflare WAF, 403 "Attention Required" to every non-browser client, from two networks | No. Real browser only; Wayback has all 2017/2020/2023 CSVs | C |
| electionresults.govt.nz `/electionresults_YYYY/xml/**` | Exempt: 200, `cache-control: public, max-age=30`, `cf-cache-status: HIT` | **Yes** (2020, 2023 live now; 2026 is 404 until the night) | C |
| mediademo.electionresults.govt.nz `/xml/` | Open Apache listing, no key | Yes; currently a running 2023-data simulation | C |
| media.election.net.nz `/xml/` | 404 (not yet populated); `/` 403 | Unknown until the night; media kit says email media@elections.govt.nz for test updates | C |
| parliament.nz, www3.parliament.nz, hansard.parliament.nz | Radware Bot Manager, hCaptcha after a few requests | No, except `hansard.parliament.nz/api/resources/daily/related/{d}/{d}-daily.pdf` | C |
| Stats NZ ArcGIS (services2.arcgis.com, owner StatsNZGeospatial) | None, CORS `*`, no key | Yes | C |
| datafinder.stats.govt.nz export/WFS | 401 without free API key | Yes with key in SSM | C |
| Wikipedia/Wikidata APIs | None; descriptive User-Agent required | Yes | C |

## 1. Electoral Commission

| Source | URL | Format | Cadence | Licence/terms | Contains | Status |
|---|---|---|---|---|---|---|
| Candidate and party lists release | elections.nz/media-and-news/2026/candidate-and-party-lists-released | HTML | one-off 9 Oct | "Copyright Electoral Commission", no CC statement anywhere on EC sites | 17 registered parties with lists, 530 candidates (443 list, 404 electorate, 65 independent/unregistered) | C (Wayback) |
| Electorate candidates 2026 | elections.nz/assets/pagecomponent-file-files/Electorate-Candidates-2026.xlsx | XLSX 31 KB, cols Name ("CHANG, Johan"), Electorate, Party, 469 rows | static | as above | every electorate candidate | C (fetched, parsed) |
| Party lists 2026 | vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf | PDF 2.3 MB, 3 pp, multi-column | static | as above | rank + name per party. No CSV yet (2023 later got Party-Lists-2023-General-Election.csv) | C |
| Register of parties and logos | elections.nz/assets/pagecomponent-file-files/Register-of-Political-Parties-and-Logos-15-July-2026.xlsx (dated filename) | XLSX | ad hoc | logos are party copyright | names, logo descriptions | C (exists) |
| Electorates (71) with centroid and bbox | vote.nz/electorate-api/electorates?type=GE&year=2025 | JSON `{id,name,type,lnglat,bounds,statsID}` | static | EC | 64 general; Maori variant unconfirmed | C via Wayback; live blocked |
| Feed reference ids | electionresults.govt.nz/electionresults_2026/xml/{electorates,parties,candidates}.xml | XML | appears election night | EC | e_no, p_no, c_no, list_no | C (404 today) |
| Enrolment by electorate | elections.nz/stats-and-research/enrolment-statistics/enrolment-by-general-electorate/?name=all (and -maori-electorate) | HTML table only | monthly | EC | per age band: eligible pop, general roll, Maori roll, total, % | C structure (2020); 2026 captures are shells |
| Maori descent / overseas enrolment | elections.nz/assets/Enrolment-stats-Maori-and-overseas/.../YYYYMMDD-Maori-Descent-Enrolment-Stats.xlsx; Overseas-Enrolment-Stats-20261001.xlsx | XLSX | monthly / quarterly | EC | by electorate | C filenames |
| Advance voting stats 2023 | elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/AdvanceVoteCSV | CSV `Date,2017,2020,2023`, daily counts | daily during advance voting | EC | **national totals only**, no electorate split | C (fetched) |
| Advance voting stats 2026 | expected vote.nz/2026-general-election/.../voting-statistics/AdvanceVoteCSV from 26 Oct | CSV | daily | EC | | I |
| Media feed documentation | 2026 media kit elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf pp.11-12 | PDF | | | "XML feed available to the media on election night", live URL `http://media.election.net.nz/xml/`; email media@elections.govt.nz for testing updates. No XSD, no rate limit, no terms published | C |
| Media feed demo | mediademo.electionresults.govt.nz/xml/ | XML, files updating every few minutes | continuous simulation | none stated | election.xml, statistics.xml, electorates.xml (72, 2023 set), parties.xml (64, 20 registered), candidates.xml (567), votingplaces.xml, eNN/eNN.xml, eNN/votingplaces/NN-NNNNN.xml | C |
| Feed schema (observed) | as above | `election.xml`: `<election updated>` + statistics (total/percent voting places counted, votes cast, electorates final, special votes) + `<partystatus><party p_no>votes, percent_votes, party_seats, candidate_seats, total_seats`. `eNN.xml`: `<electorate e_no final updated>` + statistics (informals, candidates) + `<partyvotes>` + `<candidatevotes>`. Voting place: `vp_id vp_e_no e_no vp_no updated`, `time_received`, issued ballots, party and candidate votes. `candidates.xml`: SURNAME, Given; electorate (0 = list only); party; list_no | | | | C |
| Feed public mirror | electionresults.govt.nz/electionresults_{2017,2020,2023}/xml/ | XML, 30 s cache | election night ~10 s refresh (third party); poll >= 30 s | EC | identical layout to demo; 2023 election.xml gives final seats per party (fixture) | C |
| Night cadence | media kit | | results from 7 pm, 50% places by 10 pm, 95% by 11:30 pm; preliminary site `electionresults_2026_preliminary/` then official `electionresults_2026/` 27 Nov | | progress is % of voting places, not votes | C |
| 2023/2020/2017 CSVs | electionresults.govt.nz/electionresults_YYYY/statistics/csv/<name>.csv (index statistics/index.html) | CSV, CRLF, banner rows before header | static | EC | overall-results-summary, party-votes-and-turnout-by-electorate (6 KB), candidate-votes-and-turnout-by-electorate, votes-for-registered-parties-by-electorate, winning-electorate-candidates, party-lists-of-{successful,unsuccessful}-registered-parties, party-quotients, split-votes-{all,summary,general,maori,electorate-1..72}, candidate/party-votes-by-voting-place-1..72 (E9, ~10 KB each), voting-place-coordinates (449 KB, WGS84 + NZTM) | C via browser/Wayback; 403 to curl |
| Donations over $20k (election year) | elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-exceeding-20000/; PDFs elections.nz/assets/2026-20k+-donations/<Donor>_<D>_<Month>_2026.pdf (98 files so far) | HTML table + scanned PDF | within 20 working days of receipt | EC | party, donor, amount, date | C |
| Annual donations and loans | elections.nz/democracy-in-nz/political-parties-in-new-zealand/party-donations-and-loans-by-year/; assets/Annual-Returns/YYYY/<Party>-Annual-Return-YYYY.pdf; 2025 returns released May 2026 | HTML accordion + PDF | annual, due 30 Apr | EC | | C |
| Party financial statements 2026 | elections.nz/assets/Financial-statements/2026/<Party>-Financial-Statements-2026.pdf | PDF | annual | EC | | C filenames |
| Third-party promoters 2026 | elections.nz/guidance-and-rules/for-third-party-promoters/register-of-promoters-for-the-2026-general-election/ | HTML list | as registered | EC | | C |
| Candidate expense returns | 2023: elections.nz/democracy-in-nz/historical-events/2023-general-election/candidate-expenses-donations-and-loans/ + per-candidate PDFs + summary XLSX | HTML/PDF/XLSX | 2026 due 9 Mar 2027 | EC | | C (2023) |
| Party expense returns | .../2023-general-election/party-expenses/ | HTML table + PDF | 90 working days after | EC | limit, spend, broadcasting allocation | C (2023) |
| RSS / robots | elections.nz/media-and-news/rss (media releases); robots `Crawl-delay: 2` | RSS | | | no data RSS, no JSON:API, sitemap blocked | C |

## 2. Parliament

| Source | URL | Format | Cadence | Licence | Contains | Status |
|---|---|---|---|---|---|---|
| Members of Parliament (Parliamentary Service) | catalogue.data.govt.nz/dataset/members-of-parliament; CKAN `api/3/action/package_show?id=members-of-parliament` to resolve current filenames | 3 CSVs | current list per release (11 Jun 2026); full list and terms quarterly | CC BY 4.0 | contacts CSV (Name, Title, Electorate, Party, Email; 122 rows); member-list.csv (MemberID, Name, birth/death, Gender, Ethnicity; 1,556 rows since 1853); member-terms CSV (MemberID, Parliament, Party, Date_Elected, Method, Date_Vacated, Electorate_List; 5,268 rows) | C |
| parliament.nz MP pages, photos, seat counts | parliament.nz (new Blazor SPA; `/api/opendata/...`, `/api/micrositeBaseAddresses/all` seen in browser) | JSON backend, undocumented | live | CC BY (copyright page) | blocked by Radware; no open photo source (Wikidata P18 covers 958 of 1,361 ever-MPs by name match) | C blocked |
| PCO legislation API | api.legislation.govt.nz/v0/works, /versions; docs api.legislation.govt.nz/docs/ | JSON | live, v0 beta | key by email to contact@pco.govt.nz, personal, rate limited; legislation itself has no copyright (Copyright Act s27) | search works, versions, links | C (401 without key) |
| PCO Atom feeds | mint URL via `POST legislation.govt.nz/api_keys/?id=search&legislation_type=bill` -> `api.legislation.govt.nz/rss/search?api_key=...&legislation_type=bill` | Atom, 100 entries, `x-ratelimit-limit: 1500` | as bill versions publish | CC BY site content; no copyright on legislation | per version: title, link, stage text ("Reported from the ... Committee", "Introduction") | C |
| PCO XML per document | append `.xml`, e.g. legislation.govt.nz/bill/government/2026/299/en/latest.xml (205 KB); act/public/1993/87/en/latest.xml (2.07 MB) | PCO XML, `<bill stage=...>` | per publication | no copyright | full text and stage | C |
| Hansard daily PDF | hansard.parliament.nz/api/resources/daily/related/{YYYY-MM-DD}/{YYYY-MM-DD}-daily.pdf | PDF ~600 KB | each sitting day | no copyright on Hansard | the only parliament.nz endpoint open to automation | C |
| FlavourThink/nz-hansard-scraper | raw.githubusercontent.com/FlavourThink/nz-hansard-scraper/main/data/hansard_index.json and data/days/YYYY-MM-DD.json | JSON | daily cron, last 2026-10-15; 597 sitting days 2018 to 2026-09-23 | code MIT (no LICENSE file); data no copyright | per day sections[] and plain_text | C |
| Br3nda/nz-parl-data (Hot Air) | github.com/Br3nda/nz-parl-data popolo/members.json (1.2 MB), popolo/vote_events.json (18.5 MB) | Popolo JSON | periodic, last 2026-10-05, votes to 2026-09-22 | members CC BY 4.0, votes public domain, code CC0 | 1,555 persons, 137 memberships in 54th with electorate; 16,817 party-vote events 2003 to 2026 with party tallies | C |
| Written questions | prod-win-client-writtenquestions.azurewebsites.net/written-questions (via parliament.nz) | SPA | live | CC BY | 403 to automation, no feed, no dataset | C blocked |
| Party votes | Hansard; use nz-parl-data vote_events.json or parse daily PDFs | | per sitting | no copyright | | C |
| Register of Pecuniary Interests 2026 | www3.parliament.nz/media/12156/register-of-pecuniary-and-other-specified-interests-...-as-at-31-january-2026.pdf (4.9 MB) | PDF only | annual (31 Jan snapshot, tabled 21 May 2026) | parliamentary paper, CC BY | 14 categories per MP; no machine-readable version | C |
| Wikidata 54th Parliament | query.wikidata.org/sparql; Q116674345 | SPARQL | live | CC0 | poor: 1 P39 statement with the term qualifier; not usable for membership | C |
| MP expenses | catalogue.data.govt.nz/dataset/member-of-parliament-expenses | CSV/XLSX | quarterly | CC BY | | C |
| Licence | parliament.nz/en/footer/copyright/ (Wayback) | | | CC BY for Clerk/Parliamentary Corporation content; Hansard, bills, SC reports no copyright; "misuse of parliamentary content" principles | | C |

## 3. Electorate boundaries (Representation Commission 2025, final 8 Aug 2025)

| Source | URL | Format | Licence | Contains | Size | Status |
|---|---|---|---|---|---|---|
| Stats NZ ArcGIS General Electorates 2025 | services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/General_Electorates_2025/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson | GeoJSON/JSON/PBF; no key; CORS `*`; maxRecordCount 2000 | CC BY 4.0, credit "Representation Commission, Stats NZ" | 64 features: GED2025_V1_00, GED2025_V1_00_NAME, LAND_AREA_SQ_KM (no ASCII name, no population) | HD 21.3 MB; `maxAllowableOffset=0.001` 355 KB, 0.002 222 KB; Hub shapefile 5.3 MB | C (downloaded) |
| ArcGIS Maori Electorates 2025 | .../M%C4%81ori_Electorates_2025/FeatureServer/0 | as above | CC BY 4.0 | 7 features MED2025_* | HD 4.6 MB | C |
| ArcGIS 2020 layers | .../General_Electorates_2020/FeatureServer/0, .../M%C4%81ori_Electorates_2020/FeatureServer/0 | as above | CC BY 4.0 | 65 + 7 (for 2023 baseline and boundary diff) | | C |
| datafinder General Electorates 2025 | datafinder.stats.govt.nz/layer/122741-general-electorates-2025/ | Shapefile, GeoPackage, KML, CSV, FileGDB, WFS, PMTiles; **export/WFS need free API key (401)**; metadata keyless | CC BY 4.0 | adds NAME_ASCII, GENERAL_ELECTORAL_POPULATION. No clipped/generalised variants exist | | C |
| datafinder Maori Electorates 2025 | datafinder.stats.govt.nz/layer/122742-maori-electorates-2025/ | as above | CC BY 4.0 | 7, MAORI_ELECTORAL_POPULATION | | C |
| Meshblock to electorate concordance | datafinder table 123518 Geographic Areas Table 2026 (57,575 rows; GED2025/MED2025 codes); layer 122744 2023 Census Electoral Population (MB2025 v2) | CSV (keyed) | CC BY 4.0 | the only concordances carrying 2025 electorate codes; 2025-vintage tables still carry GED2020 | | C |
| Representation Commission report | elections.nz/democracy-in-nz/historical-events/boundary-review-2025/report-of-the-representation-commission-2025/ | HTML + PDF schedules | Crown | abolished Ohariu, Mana, Otaki; created Kapiti, Kenepuru; renamed Te Atatu->Henderson, Kelston->Glendene, New Lynn->Waitakere, Panmure-Otahuhu->Otahuhu, Bay of Plenty->Mt Maunganui, East Coast->East Cape, Wellington Central->Wellington North, Rongotai->Wellington Bays | | I (press + attribute diff C) |
| LINZ Data Service | data.linz.govt.nz | | | no electorate layers | | C |
| GitHub pre-built GeoJSON | tuttinator/nz-electorates (MIT, 2014), bradleyscott/election-night (no licence, pulls the ArcGIS service) | GeoJSON | | **no licensed 2025 GeoJSON/TopoJSON exists**; build and publish your own | | C |

## 4. Stats NZ census by electorate

| Source | URL | Format | Licence | Contains | Status |
|---|---|---|---|---|---|
| Number of electorates and electoral populations: 2023 Census | stats.govt.nz/assets/Uploads/Number-of-electorates-and-electoral-populations-2023-Census/Download-data/number-of-electorates-and-electoral-populations-2023-census.xlsx | XLSX 43.5 KB | CC BY 4.0 | quotas, electoral population per electorate | C |
| 2023 Census electorate profiles | none: stats.govt.nz/tools/2023-census-place-summaries/ 404; Aotearoa Data Explorer (api.data.stats.govt.nz, SDMX, free key) has 335 census dataflows, **zero by electorate** | | | | C |
| ArcGIS 2023 Census SA1 totals by topic | services2.arcgis.com/vKb0s8tBIA3bdocZ/arcgis/rest/services/2023_Census_totals_by_topic_for_individuals_by_SA1/FeatureServer/0 (households, dwellings, SA2 siblings) | JSON, paginate 2000 | CC BY 4.0 | 32,817 SA1 x 530 coded fields; aggregate to electorates via concordance (random rounding base 3 makes sums approximate) | C |
| Parliamentary Library "Electorate data 2023" | www3.parliament.nz/en/mps-and-electorates/electorate-data-2023/ | XLSX (snippets: "2023 Census Data by General Electorate (2025 Boundaries)", Maori equivalents, "2023 Election Results") | CC BY (inferred) | the closest ready-made profile set; Radware-blocked, needs a browser to fetch once | I |
| Attribution wording | datafinder.stats.govt.nz/license/attribution-4-0-international/ | | CC BY 4.0 | "Source: Stats NZ and licensed by Stats NZ for reuse under the Creative Commons Attribution 4.0 International licence." | C |

## 5. Opinion polls

| Source | URL | Format | Cadence | Licence/terms | Contains | Status |
|---|---|---|---|---|---|---|
| Wikipedia opinion polling page | en.wikipedia.org/wiki/Opinion_polling_for_the_2026_New_Zealand_general_election; API `w/api.php?action=parse&page=...&prop=wikitext&format=json&formatversion=2` (136 KB); REST `api/rest_v1/page/html/...` (CORS `*`, `content-revision-id` header) | wikitext / Parsoid HTML | edited within hours of each poll (rev 2026-10-16) | CC BY-SA 4.0; UA policy `name/ver (contact)`; serial requests, `maxlag` | party table (Date, Pollster, Sample, NAT, LAB, GRN, ACT, NZF, TPM, OPP, Others, Lead; rows carry `data-sort-value`; event rows `colspan=11`), 12 electorate polls, Maori roll, preferred PM, approval, `Template:2026 NZ election forecasts` with per-poll seat projections | C |
| 1News-Verian | 1news.co.nz/tags/verian-poll/; RSS 1news.co.nz/arc/outboundfeeds/rss/?outputType=xml; full reports on Scribd | article + PDF | fortnightly in campaign (23-27 Sep, 1-5 Oct, 8-12 Oct) | robots allow; blocks AI UAs | headline numbers | C |
| RNZ-Reid Research | rnz.co.nz/news/politics/556774/...; RSS rnz.co.nz/rss/political.xml | article + Datawrapper | ~quarterly | `Crawl-delay: 7`; terms forbid copying and RSS aggregation; AI mining prohibited. Link only | | C |
| Taxpayers' Union-Curia | taxpayers.org.nz/polling_archive; **RSS taxpayers.org.nz/polling_archive.rss**; curia.co.nz/feed/ | HTML, random slugs | monthly + electorate polls | permissive robots, no scraping clause | party vote, seat projection, PM, direction | C |
| Roy Morgan | roymorgan.com/morgan-poll/new-zealand-party-voting-intention (HTML table 1996 to now); monthly findings + S3 PDF | HTML + PDF | monthly, first week after | 2013 terms ban scrapers and systematic downloading; take via Wikipedia | | C |
| Freshwater Strategy / The Post | freshwaterstrategy.com/2026/09/15/...; XLSX wp-content/uploads/Data-Tables-The-Post-Freshwater-Strategy-NZ-Polling-September-2026-1.xlsx (179 KB) | post + XLSX crosstabs | ~monthly | none stated | full tables | C |
| Talbot Mills / Anacta | private (talbotmills.com -> anacta.com); numbers leak via The Post | news only | monthly | subscription | | C |
| Horizon, Whakaata Maori-Curia | horizonpoll.co.nz/News; curia.co.nz/2026/09/te-tai-tonga-poll-3/ | HTML | ad hoc | | Maori roll and electorate polls | C |
| NZ Herald-Motu poll of polls | nzherald.co.nz/nz/herald-motu-research-poll-of-polls-... | premium articles, no data | daily rerun | NZME terms ban systematic download; robots bans ML | government probability, OPP threshold | C (paywalled) |
| The Post election dashboard / Stuff Flip Forecaster | thepost.co.nz/election-dashboard; stuff.co.nz/politics/361030311/... | JS, 403 headless | per poll | Stuff terms ban datasets and ML | poll of polls, uniform swing, donations, Polymarket | I |
| Newsroom charts | newsroom.co.nz/2026/04/30/the-latest-charts-and-data-on-election-2026/ | Flourish embeds | per poll | | 60-day average, seats, donations | C |
| The Progress Report (ex polled.co.nz) | theprogressreport.co.nz/poll-graph, /mmp-calculator; internal api/poll-data 404 unauthenticated | JS | ongoing | copyright, closed | | C |
| Polymarket Gamma | gamma-api.polymarket.com/events?slug=next-prime-minister-of-new-zealand-174 (+ nz-election-national-party-of-seats, nz-election-labour-party-of-seats, new-zealand-election-turnout, which-parties-will-be-part-of-the-next-government-of-new-zealand, ...) | JSON, no auth | live | Polymarket ToS | prices, volumes ($3k to $43k) | C |
| Manifold | api.manifold.markets/v0/search-markets?term=new%20zealand%20election | JSON | live | public | ~10 play-money markets | C |
| Kalshi | api.elections.kalshi.com/trade-api/v2/events?status=open | JSON | | | no NZ market | C |
| ellisp/nzelect | github.com/ellisp/nzelect | R, GPL-3 | not a 2026 forecaster | GPL-3 | historical results by voting place | C |

## 6. Policy and candidate information

| Source | URL | Format | Licence/terms | Contains | Status |
|---|---|---|---|---|---|
| Policy.nz 2026 (The Spinoff) | policy.nz/2026; data SSR-embedded in `<script id="__NEXT_DATA__">` (health topic 185 KB JSON: parties, policies with citations, candidates); sitemap policy.nz/api/sitemap/2026.xml; no public API | Next.js JSON | **terms: personal use only; commercial/professional use and derivative works prohibited; licence via contact@policy.nz** | 17 parties, ~50 topics, candidates per electorate | C |
| Vote Compass 2026 | votecompass.tvnz.co.nz / votecompass.1news.co.nz (live since 4 Oct, 30 propositions) | closed SPA | no export | user alignment only | C |
| Party policy pages | national.org.nz/policies, labour.org.nz/policy, greens.org.nz/policy, act.org.nz/policies, nzfirst.nz/policy, maoriparty.org.nz/policies (429 on repeat), opportunity.org.nz/policy | HTML, unstructured | party copyright | | C |
| Wikipedia candidates page | en.wikipedia.org/wiki/Candidates_in_the_2026_New_Zealand_general_election_by_electorate | wikitext `{{NZ election box candidate|party=|candidate=|list=|notes=|sources=}}`, 503 boxes, 71 sections | CC BY-SA 4.0 | party, candidate, list rank, sources | C |
| Wikidata candidacies | query.wikidata.org/sparql; election item Q104843407; P3602 with qualifiers P102 party, P768 electorate, P1545 list position | SPARQL JSON | CC0 | 530 people, 912 candidacy statements | C |
| EC Electorate-Candidates-2026.xlsx | see section 1 | XLSX | EC | official names | C |

## 7. Comparable apps and dashboards

| Name | URL | What it showed | Open? | Status |
|---|---|---|---|---|
| NZ Herald 2023 interactive | nzherald.co.nz/nz/track-nz-election-2023-live-results-with-nz-heralds-interactive-map/... | party vote, electorate map, flipped seats, margin grid | closed | C |
| NZ Herald 2026 Motu poll of polls | see 5 | probabilistic forecast | paywalled | C |
| RNZ | Reid Research hub, Datawrapper | poll charts, seats, PM, favourability | closed | C |
| Stuff / The Post | Flip Forecaster, election dashboard, "Aotearoa Decides" night special | seat flips, overhang, poll average, donations, Polymarket | closed | I |
| The Spinoff 2023 | hex map (5 hexes per electorate, bloc lean) thespinoff.co.nz/politics/04-11-2023/...; live blog | hex map, bloc totals; no 2026 tracker found | closed | C |
| 1News/TVNZ | Vote Compass; election night special 7 pm 7 Nov | | closed | C |
| Newsroom | Flourish page | poll trend, seats, donations tally | closed | C |
| ResultsDesk.nz (independent) | resultsdesk.nz; bundle pub-f6186e26b12c470f9caf26d081720063.r2.dev/results-bundle.json (357 KB) | Leaflet map on Stats NZ boundaries, seats, sortable electorate table, coalition strip; consumes the mediademo feed | JSON exposed, no licence, no source | C |
| The Progress Report | theprogressreport.co.nz | MMP and caucus calculators, swing map, poll DB, candidates, ad tracker | closed | C |
| Electoral Commission MMP calculator | elections.nz/stats-and-research/mmp-seat-allocation-calculator/ | official Sainte-Lague tool | blocked headless | I |
| GitHub | ellisp/nzelect (GPL-3, maintained); bradleyscott/election-night (collector + mock server for the XML feed, pushed 2026-10-12, no licence); wombleton/saintelague (JS, no licence); oscarcs/MMP-calculator (MIT, 2017); dakvid/election2017, thoughtfulbloke/nzes stale | | mixed | C |

White space: no open-data, open-source poll tracker with downloadable CSV and a published method; no threshold watch for OPP/NZF/TPM across pollsters; no polls-vs-markets view; no pollster scorecard against 2020/2023; no electorate page joining candidates (Wikipedia/Wikidata/EC XLSX), 2023 baseline, electorate polls and swing; no open election-night client built on the XML schema with a preliminary-to-special waterfall; no coalition explorer honouring stated exclusions; no tracker that shows provenance per number.

## 8. MMP seat allocation (authoritative references)

| Source | URL | Content | Status |
|---|---|---|---|
| Electoral Act 1993 s191 | legislation.govt.nz/act/public/1993/87/en/latest/#DLM310034; XML .../latest.xml (reprint 1 Jan 2026) | s191(4) disregard a party with under 5% of **all** valid party votes and no electorate seat; (5) divisors 1, 3, 5, 7, ... every odd number; (7) highest 120 quotients, or fewer per (8); (8) deduct independents and unlisted-party electorate winners from 120; (9) ties by lot | C |
| s192 | ...#DLM310042 | seats = circled quotients; deduct electorate seats won; (5) electorate seats >= entitlement means no list seats, electorate seats kept (**overhang**) | C |
| s193 | ...#DLM310045 | list filled top-down skipping electorate winners; exhausted list leaves seats empty | C |
| EC Sainte-Lague explainer | electionresults.govt.nz/sainte_lague.html; electionresults_2023/statistics/sainte-lague-formula.html | worked 2014 example | C (browser) |
| 2023 fixture | electionresults_2023/statistics/csv/party-quotients.csv (Wayback) and electionresults_2023/xml/election.xml (curl OK) | valid party votes 2,851,211; NAT 1,085,851 -> 43+5=48; LAB 767,540 -> 17+17=34; GRN 330,907 -> 3+12=15; ACT 246,473 -> 2+9=11; NZF 173,553 -> 0+8=8; TPM 87,844 (3.08%, qualifies via electorates) 6 electorate, entitlement 4, **2 overhang**; TOP 2.22% -> 0; House 122 (123 after Port Waikato by-election) | C |
| Reusable code | juliuste/sainte-lague (ISC, divisor primitive only); nzelect allocate_seats (GPL-3); wombleton/saintelague (no licence) | implement s191-193 directly (~40 lines) and test against the 2023 quotients | C |

## Gaps and risks

1. **Nothing results-related exists for 2026 before 7 pm 7 Nov**: `electionresults_2026/` and its `/xml/` are 404; `media.election.net.nz/xml/` is 404. Only the 2023-data demo exists; all `e_no`/`p_no`/`c_no` ids will change and 2026 has 71 electorates (e01..e71). Build id maps from live `electorates.xml`, `parties.xml`, `candidates.xml` at startup.
2. **Cloudflare/Incapsula/Radware**: elections.nz, vote.nz, parliament.nz and the HTML/CSV side of electionresults.govt.nz cannot be fetched from GitHub Actions. Fetch historical CSVs once (browser or Wayback) and commit as fixtures. Only `/electionresults_YYYY/xml/**` (30 s cache, poll >= 30 s), the demo host, Stats NZ ArcGIS, PCO, data.govt.nz, Wikipedia/Wikidata, Polymarket and the pollster RSS feeds are reliably scriptable. Risk: the XML exemption is a WAF rule that could change on the night; the media feed needs an email to media@elections.govt.nz for test access.
3. **No per-electorate advance-voting series** (national daily CSV only, 2026 endpoint not yet created); enrolment is a monthly HTML table with no CSV.
4. **No official 2023 Census product by 2025 electorate**; options are the Parliamentary Library XLSX (browser fetch, inferred) or aggregating SA1 totals via the keyed datafinder 2026 concordance (approximate due to random rounding).
5. **Licence**: EC sites carry only "Copyright Electoral Commission", no CC statement; attribute and link, do not claim open licence. Policy.nz forbids derivative works without a commercial licence. RNZ, NZ Herald, Stuff and Roy Morgan terms forbid scraping or dataset building: link only, take poll numbers via Wikipedia (CC BY-SA, share-alike applies to the derived table). Wikipedia is editor-maintained, so parse defensively (event rows, footnotes, ties, new pollsters such as Anacta).
6. Rate limits: Wikimedia asks for a descriptive User-Agent and serial requests; PCO Atom `x-ratelimit-limit: 1500`; maoriparty.org.nz returned 429 on a second hit; datafinder and PCO JSON API keys are personal (keep in SSM). GitHub API limits were hit during research; use raw.githubusercontent.com for the Hansard and Hot Air datasets.
7. Dependency risk: FlavourThink and Br3nda datasets are single-maintainer; ResultsDesk's R2 bundle is unlicensed. Hansard, votes and WPQ are quiet until the 55th Parliament opens (dissolution 1 Oct; writ return by 3 Dec), so Parliament data is background for this app.
8. Current MP CSVs refresh quarterly, so the post-election House must be computed from results XML plus the party lists until the Parliamentary Service updates.

## Three app concepts

**A. Open Poll-to-Seats Tracker.** Hourly Action parses the Wikipedia poll table and forecast template, runs a house-effect-adjusted average and the s191-193 allocator, and publishes CSV/JSON plus a threshold-watch for OPP/NZF/TPM and a Polymarket seat-band overlay. Every number links to its source row and the Action run that produced it. Distinct from Herald/Post/Stuff because the data, method and code are open (CC BY-SA on the derived table).

**B. 71 Electorates.** One page per electorate built from Stats NZ ArcGIS boundaries (simplified, CC BY), 2023 E9 voting-place results re-cut to 2025 boundaries where possible, the EC candidate XLSX joined to Wikipedia/Wikidata candidate boxes, the 12 electorate polls, uniform-swing projection, and a boundary-change diff against 2020. On the night it switches to the `eNN.xml` feed with voting-place dots on the map; a mode no media outlet shipped openly.

**C. Election Night Replay and Live Desk.** A client for the XML schema that today replays the mediademo simulation (and the 2017/2020/2023 archives, which are curl-able) at adjustable speed, showing a seat waterfall from first count through overhang and specials, and on 7 Nov points at `electionresults_2026/xml/` polling every 30 s. Ships the 2023 `party-quotients.csv` as a test fixture, the allocator as a library, and a "what would change with specials" slider; publishes the collected snapshots as a public dataset afterwards.

No repository files were modified. Scratch material from the research sits under `/tmp/nzelect`, `/tmp/nzres`, `/tmp/nzec`.
