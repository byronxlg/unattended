# NZ election feed home implementation plan

## Scope and working rules

Implement H1-H12 from `intent/nz-election/home.md` in two PRs. The feed, shared components, joins and regression coverage are likely to exceed 1,200 changed lines once per-route OG output and browser coverage are included. Keep the feed and its social join together; follow with night, electorate ordering and OG delivery.

Read root and product `AGENTS.md` before implementation. Work only in the assigned `change/*` worktree; commit locally, never push or edit `main`. No changes to data families, captures, publication ownership, credentials or runtime dependencies. Markets and daily automation remain increment 7 of `plan-m2.md`, a separate change.

`home.md` resolves layout conflicts; `design.md` supplies the shipped tokens and checks; supervisor resolutions override the older spec. Retain standard-library Python, exact arithmetic, static rendering and the existing system font stack.

This plan comes from read-only inspection. No builds, tests or screenshots were run. Commands and PASS lines below are acceptance contracts, not observed results. Paths below are relative to `product/nz_election/` unless stated otherwise.

## Current routes, fragments and count pins

The current registry has seven primary routes: `/`, `/electorates/`, `/night/`, `/campaign/`, `/downloads/`, `/methods/`, `/social/poc/`; 71 detail routes bring the total to 78. Add `/polls/`, giving eight primary routes and **79 routes**. All public paths retain `/unattended/nz-election/`.

`web/templates/polls.html:1-5` contains placeholders only, with no literal IDs. Today's home IDs are supplied by `base.html`, `source-note.html` and Python:

| Existing ID or fragment | Definition and consumers | Destination |
|---|---|---|
| `main` | `web/templates/base.html:13,15`; `tests/screenshots.py:100` | Keep on every page |
| `source-seats` | `pipeline/build.py:156,204-213,245`; `tests/test_design.py:120`; `tests/screenshots.py:197`; `tests/coalitions_browser.py:72,125` | Keep on home and polls |
| `coalition-explorer`, `coalition-title` | `pipeline/build.py:236-237`; `web/coalitions.mjs:201`; `tests/coalitions_browser.py:29,64,157,205`; `tests/screenshots.py:123` | Move to polls |
| `source-average` | `pipeline/build.py:284-294` | Keep on polls; reuse for home polling module |
| `source-thresholds` | `pipeline/build.py:295-306`; `tests/test_increment_two_regressions.py:90` | Keep on polls and shared home seat module |
| `source-history` | `pipeline/build.py:312,317-319` | Move to polls |
| Each published poll's `id` | `pipeline/build.py:313` | Move every value to polls |
| `source-<poll.id>` | Definition `pipeline/build.py:312`; links at `:311` | Move every value and link to polls |
| Dynamic source-note ID | `web/templates/source-note.html:1`; supplied by `build.source_note()` | Preserve caller-selected IDs |
| `#coalition=<encoded state>` | `web/coalitions.mjs:167-194`; `tests/design_states.py:59-63`; `tests/test_coalitions.py:75-88`; `tests/coalitions_browser.py:108-114` | Polls URL state, not an HTML ID |

There are currently no literal `seats`, `polls` or `explorer` IDs. Add these required anchors explicitly: `seats` and `polls` on both pages, `explorer` wrapping the polls explorer while preserving `coalition-explorer`. Do not claim nonexistent old anchors were discovered.

Other existing template and shared fragment targets stay on their current routes:

- `map-general`, `map-maori`, `electorate-search`, `search-result`: `web/templates/electorates.html:3-8`; browser consumers at `tests/screenshots.py:337-350`.
- `electorate-<slug>`: `pipeline/build.py:400`; hash consumer `web/electorates.mjs:31-32`.
- `map-title`, `map-description`, `selected-hatch`: `pipeline/geography.py:168-169`; synthetic map-fragment coverage at `tests/test_geography.py:103`.
- `candidates-title`: `web/templates/electorate.html:5`.
- `source-geography`: `pipeline/build.py:405`; electorate sources `source-electorates`, `source-candidates`, `source-baseline-2023`, `source-enrolment`, `source-electorate-polls`: `pipeline/electorate_pages.py:29-30` and template references.
- `source-polls`: default `pipeline/build.py:82`, used by methods/downloads and `web/templates/methods.html:2-14`.
- `source-social`, `source-social-attitude`, `social-method`: `pipeline/social_page.py:34,40,76,82`. Home's social method link must target `/social/poc/#social-method`, not an absent local fragment.
- `source_note()` has a bare `#` fallback at `pipeline/build.py:106`; new notes must not manufacture missing input links.

Generate the old poll-ID inventory from a validated fixture bundle in tests, then assert every ID and source link resolves on `/polls/`. Preserve the inventory rather than hardcoding fixture-specific poll IDs in templates.

### Route and image pins

| Location | Current contract | Required change |
|---|---|---|
| `config/routes.json:3-4` | Root labelled “Polls and seats” | Root “Home”; add `polls/` with old label |
| `pipeline/build.py:5,459,509` | 78 pages; seven primary routes; printed 78 | 79 pages; eight primary routes; `PASS build: 79 routes` |
| `tests/test_build.py:39-41` | Exact route-derived HTML set | Explicitly assert 79 and exact set |
| `tests/test_design.py:85-87` | Exact route-derived HTML set | Same 79-route assertion |
| `tests/test_electorates.py:116-119` | 71 details plus exact route-derived set | Keep 71; total becomes 79 |
| `tests/test_verify_supplied.py:37`; `pipeline/verify.py:186` | 71 electorate details | Unchanged |
| `tests/test_geography.py:29` | 77 correspondence entries | Unchanged: this is not a route count |
| `tests/test_contracts.py:21` | 111 immutable captures | Unchanged: no new captures |
| `tests/screenshots.py:273-277,380-383` | Registry-derived route coverage | Assert 79 unique routes |
| `tests/screenshots.py:300,307` | Two sizes for all routes; eight routes at 360 | Add polls to 360 subset: nine |
| `tests/screenshots.py:315` | Root filename defaults to `polls` | Rename root to `home`, avoiding collision |
| `tests/design_states.py:11-14`; `tests/screenshots.py:142` | 16 states twice, coherent state also at 360 | Preserve 33 images |
| `tests/screenshots.py:328-372` | Names image, map layers/focus and missing detail | Preserve 13 populated-data images |
| `tests/screenshots.py:208-228` | Dark home, skip focus, main focus | Preserve three; add home-row keyboard focus |
| `tests/screenshots.py:233-256,266` | Two OG specimens | Replace with one OG per route, 79 |
| `tests/screenshots.py:388` | Prints total images, not just baseline | Print exact new total |

Current populated total: 156 baseline + 8 narrow + 33 states + 13 map/detail + 3 home extras + 2 OG = **215**.

Final populated total: 158 baseline + 9 narrow + 33 states + 13 map/detail + 4 home extras + 79 OG = **296 images**. This replaces the two old OG specimens; do not double-count them. `--og-only` produces 79 images. Counts describe manifest records, not duplicate copies of PNGs.

## Rendering architecture

Extract presentation logic from `build.polls_page()`, not merely from the five-line template. Keep `home_presentation()`, `default_scenario()`, `home_sentence()`, `strip()` and their stale/allocation decisions as the shared calculation path.

Add `web/templates/seat-module.html`, `party-rows.html` and `threshold-watch.html`. The seat module composes the existing proportional strip, party rows/table, assumptions disclosure, unresolved-tie text and threshold watch. Both home and polls call the same renderer with the same presentation object. Keep the existing strip CSS and client/server strip parity test.

Use one enclosing source-note component for the shared seat module, retaining `source-seats` and an internal `source-thresholds` target with the threshold-specific explanation. Preserve source text, inputs, fieldwork dates and run links. Figures and numeric groups reference the relevant targets. Do not duplicate IDs or repeat an entire source catalogue for each party.

Keep the poll history, average details, missing observations, exclusions, individual sources and explorer on `/polls/`. Preserve their content and source targets; only factor shared rendering and add section anchors.

Add `web/templates/home.html`, rendered in this order:

1. Home-only section links: Polls, Seats, Electorates, Night, Social.
2. Hero: “New Zealand votes on 7 November 2026”, build-time countdown, updated time, existing generated seat sentence, compact jump list.
3. `#seats`: “Seats from current polls”, shared seat module and legend disclosure.
4. `#polls`: “Where the party vote stands”, two leading averages, remaining figures, fieldwork, pollster count, source and “All polls”.
5. Links to `/methods/` and `/polls/#explorer`; optional future market panel within the polling section.
6. `#electorates`: “Electorates to watch”, selection explanation and six ledger rows.
7. `#directory`: “All 71 electorates”, compact directory.
8. `#social`: “What people are posting”, primary-party chart and proof-of-concept disclosure.
9. `#method`: “How this site calculates seats”, three short paragraphs and scoped licence line.

Add `#night` to the hero's results/countdown destination, with a clear `/night/` link, so all five section tabs are genuine home anchors. Use normal links, not ARIA tab widgets. The selection tick follows the targeted section through CSS; no scroll-tracking script.

Separate document title, visible heading and description in `base.html`. Home's seat sentence becomes framing prose instead of its current `<h1>`. Keep exactly one `<h1>`, `main`, skip link and existing footer on every route.

## Data joins and unavailable states

### Countdown and hero

Add pure `election_countdown(built)` to the presentation layer. Validate the canonical UTC timestamp, convert with `ZoneInfo('Pacific/Auckland')`, subtract its calendar date from `date(2026, 11, 7)`, and return display state and day count.

Three fixed-time tests:

- `test_countdown_before_nz_midnight`: `2026-11-06T10:59:59Z` gives “1 days until election day”, or grammatically singular “1 day until election day”.
- `test_countdown_on_election_day`: `2026-11-06T11:00:00Z` gives “Election day”.
- `test_countdown_after_election_day`: `2026-11-07T11:00:00Z` gives “Results”, never a negative count.

Test the helper directly during frozen instants; do not bypass `require_publication_allowed()` to build those pages. Use the same helper for night. Label build time separately from source observation and acquisition times. No client countdown.

With absent polls, retain “No data yet. Polls are checked hourly.” and the no-seat sentence. With stale/incomplete seats, retain the existing reason and dated polls; do not show a stale strip as current.

### Poll figures

Use the latest `averages.data` row's `descriptive[party_id]`, including each entry's `value`, `scale` and contributing `poll_ids`. Use existing `average.display()` for one-decimal, half-up formatting. Sort exact values descending with party ID as deterministic tie-breaker; choose the two largest named parties, keeping Others in the remaining row.

Join `average.poll_ids` to `polls.data[].id`; derive the fieldwork interval from minimum `fieldwork_start` and maximum `fieldwork_end`. Count distinct published `pollster` values, not poll rows. Disclose unequal per-party coverage and missing observations.

Use `source_note(..., identity='source-average', inputs='averages.json', contributing_polls=selected)` with the pinned Wikipedia revision/history, CC BY-SA 4.0, retrieval date and calculation links. No interpolation or trend arrows. Missing averages render “Not available” with the family/status reason; missing individual values are not zero.

### Electorates to watch

Add a shared `electorate_summary(row, envs, correspondence)` helper for home rows, detail descriptions and OG text.

Join current registry `stats_id` to correspondence `entries[].new_id`; join its single `old_ids` member to `baseline-2023.data[].old_electorate_id`. Cross-check registry `baseline_ids`. Preserve exact string IDs, including leading zeroes.

Eligibility is unchanged boundaries, not merely unchanged names: include `relationship == 'unchanged'` and the reviewed East Cape rename (`new_id == '008'`, old ID 9), whose unchanged boundaries are explicit at `config/electorate-correspondence.json:203-219` and supervisor totals at `:50,67`. Exclude other renamed, changed, created or unresolved entries.

Require at least two `candidate_votes` rows and a unique highest vote total. Sort candidates by integer `votes`; margin is winner votes minus runner-up votes. Winner's `party` supplies held-by wording, not `party_votes`. Rank by `(margin, current registry id)` and take six. Publish this rule beside the module and disclose missing baseline exclusions.

Display current `name` and `slug`, then “Held by {party}, {margin:,} votes in 2023 on the original boundaries”. This is a historical statement, not a current-officeholder claim.

Join `candidates.data[].electorate_id` to current registry `id`; display published `name` and `party_id`, preserving source conflicts. Show all published electorate candidates in deterministic party/name/ID order; do not invent a ranking or silently omit minor parties. Use neutral outlined marks unless an explicit existing identity mapping supports a party colour.

**Omit incumbent markers.** Published baselines contain names, parties and votes, while current `person_id` values and reviewed mappings do not establish continuing incumbency. Do not join by name similarity. Amend H5 in `intent/nz-election/home.md` to record this permitted departure.

If baseline or candidates is absent, render one “Not available: {reason}” module state, not six empty rows. An empty candidate list for an otherwise selected electorate gets explicit row-level unavailable copy. Fewer than six eligible baselines yields the available rows and an explanation, never changed-boundary substitutes.

### Directory and methods

Render all 71 current registry entries, falling back to reviewed `config/electorates.json` when geography is unpublished. Link their stable slugs. Show historical held-by marks only where the summary join is supported; changed-boundary rows say “Boundary changed; 2023 holder not comparable”, unresolved rows say so explicitly.

One directory source note combines registry/correspondence and baseline provenance. Do not embed the national map or 71 outlines on home. Missing baseline data leaves the complete directory with “Held-by information not available”.

The method module explains equal-weight polling, threshold/Sainte-Laguë allocation, and electorate/list-capacity assumptions in three paragraphs. Link `/methods/` and available inputs. State poll-derived CC BY-SA separately from Electoral Commission restrictions. It remains useful without published polls.

### Social

Extract the primary-party aggregate and chart renderer from `pipeline/social_page.py`; the POC currently has multiple charts, so choose its first, “Primary-party share of sampled posts”.

Read only `social/daily.data`: sum `party_counts` and `sample.eligible`, use minimum/maximum `day`, and preserve retrieval information from `provenance.windows[].retrieved_at`. Reuse the existing table equivalent, party labels, under-five suppression, under-20 percentage withholding and synthetic-fixture label.

Home renders the last published aggregate with its actual date even after 36 hours, as H9 requires. Keep the POC page's existing stale-withholding policy and tests by separating aggregate rendering from page availability policy. Home gets dated/overdue copy, not a new freeze gate.

Absent or empty aggregate renders “Not available: no published sample” plus any safe status reason. Every state retains a source note and POC link. Never render credits, raw posts, handles or identifiers.

### Markets

No market family exists in current `export.FIELDS`, `FAMILIES` or `ALLOWED`. Do not read an unvalidated side file or widen those allowlists here. Reserve an optional renderer hook inside `#polls`; absence renders no market panel and never breaks home. Increment 7 owns schema validation and the populated adapter, including its observation date, terms and unavailable state.

## Night, electorate pages and OG output

Add `night.html`: countdown/results line; “Results appear here from 7 pm on 7 November”; explanatory copy for places counted, seat waterfall and party table; no fabricated numeric placeholders. Include the publication-freeze sentence, Electoral Act s197 source and official `https://www.electionresults.govt.nz/` link. After polling day use “Results” and honest availability copy until M3 supplies results.

`electorate.html:2-5` currently places boundary copy and outline before candidates. Move candidates first in DOM and visual order, then the shared historical summary, then boundary note/outline, original results, enrolment and local polls. Use summary-specific unavailable/comparison wording on unsupported boundaries. Document titles and OG descriptions include electorate name and supported historical held-by party, never an invented holder.

Add a shared route-key helper: root becomes `home`; otherwise strip trailing `/` and replace internal `/` with `--`. Examples: `polls`, `social--poc`, `electorates--wellington-north`. Assert uniqueness across 79 routes.

Build renders `og.html` variants into non-route files such as `og/home.html`, plus a site-owned manifest of route, key, title, description, HTML and PNG paths. Do not create additional `index.html` routes. Variants:

- Home: existing seat sentence and shared strip, or explicit unavailable sentence.
- Polls: two leading average figures and poll source.
- Electorate: name and historical held-by line, or explicit comparison/unavailable text.
- Other routes: page title and relevant source/availability note.

Add `og:image`, `twitter:image`, description and 1200×630 dimensions to `base.html`. Use absolute URLs rooted at `https://byronxlg.github.io/unattended/nz-election/og/<key>.png`. Compute references deterministically; `build.py` never launches a browser.

`screenshots.py` consumes the built OG manifest, renders each local HTML at 1200×630 and writes `site/nz-election/og/<key>.png`. Record hashes and paths in the screenshot manifest; optional artifact copies do not increase counts. Preserve loopback-only requests, axe checks and explicit overflow/clipping checks. `--og-only` must process all 79 routes.

## CSS and navigation

Extend only `web/styles.css`, using existing tokens. Modules have a single ink rule above, 20px heading, no filled container, radius or shadow. Poll figures and countdown use 40px tabular type; party colours are outlined fills beside ink labels.

Use one electorate column below 800px and two at/above 800px. Directory is one column below 800px and four at/above 800px. Keep 16px phone gutters, 24px desktop gutters and 1120px maximum width. Place countdown below title on phones and beside it on desktop. Section links scroll horizontally within their own container, never the page.

Preserve 44px targets, visible focus, dark tokens, reduced motion and zero load animation. Compact source actions without shrinking targets. Keep the seat provenance fold check at 360/390; adjust spacing and disclosures rather than deleting the check.

Both desktop and phone nav are generated from `config/routes.json` through `build.py:465-466` and `base.html:14`. Every page gets Home plus Polls and seats at `/polls/`; other destinations remain. Test both copies, active primary page, detail-page behavior and absence of section tabs away from home.

## Verification and test inventory

Add these focused tests:

| File | Principal functions |
|---|---|
| `tests/test_home.py` | `test_home_module_order`, `test_poll_fragments_preserved`, `test_shared_seat_module_identical`, `test_poll_figures_and_coverage`, `test_home_missing_families`, `test_home_navigation`, `test_home_html_css_budget` |
| `tests/test_home.py` | Three countdown tests named above; `test_watch_selection_and_boundary_exclusion`, `test_watch_missing_and_tied_baselines`, `test_no_inferred_incumbents`, `test_directory_all_71`, `test_home_social_retains_dated_aggregate` |
| `tests/test_home_routes.py` | `test_night_copy_and_transition`, `test_electorate_candidates_first`, `test_electorate_metadata`, `test_og_manifest_and_absolute_urls`, `test_og_variants_and_unique_keys`, `test_screenshot_count_inventory` |

Budget test: built home UTF-8 HTML bytes plus linked CSS bytes must be **under 200,000** on populated and unavailable builds. Preserve CSS under 12,000 and existing compressed first-view/font-reservation budgets. Update `test_design.py:109` because explorer assets now belong to polls; assert their absence from home dependencies and presence on polls.

Retarget history/injection/explorer assertions in `test_build.py`, `test_coalitions.py`, `coalitions_browser.py` and `verify_polls`/`verify_coalitions` to `/polls/`. Keep equivalent home availability tests. Move explorer design-state routes and hashes to polls; change direct-child strip selectors at `screenshots.py:175,180` to the shared seat container without weakening availability checks.

Add verifier checks `home` and `home-routes` to both CLI choices and registry. `home` validates joins, fragments, module order, source targets and budgets; `home-routes` validates night, electorate order and OG metadata. With `--site`, inspect supplied pages, not only temporary fixtures.

`MISSING_SOURCE` currently belongs to `tests/design_checks.py:27`, not the verifier registry. Reuse that parser in the new verifier checks. `SMALL_TARGET` is a browser geometry assertion at `screenshots.py:95`; retain it on home and every route rather than claiming Python verifies target dimensions.

Final `verify.py all` must print existing `PASS polls`, `PASS thresholds`, `PASS provenance`, `PASS pipeline`, `PASS coalitions`, `PASS geography: 64 general, 7 Māori`, `PASS candidates: 71 electorates`, `PASS electorates: 71 pages`, `PASS social`, then `PASS home`, `PASS home-routes`, and `PASS all`.

Host preparation uses fresh worktree-local artifact directories: run `refresh.py --fixtures`, `daily_refresh.py --out`, then `social.py --fixtures --day 2026-10-16 --now 2026-10-17T01:00:00Z`, all against the same bundle. For populated seat screenshots, add a small fixture-only preparation helper using the existing `refresh(..., end_date='2026-07-18', now=...)` API; do not alter production refresh or impute Others. Build with matching `--now`. Record the historical/synthetic demonstration basis.

Host-run commands, using installed Chromium and cached dependencies:

```sh
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election --now 2026-10-17T01:00:00Z
uv run product/nz_election/pipeline/verify.py all --data artifacts/nz-election/data --site site
uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots
uv run product/nz_election/tests/coalitions_browser.py --site site
```

Expected lines: `PASS build: 79 routes`, `PASS all`, `PASS screenshots: 79 routes, 296 images`, `PASS coalition browser`. OG-only command adds `--og-only` to screenshots and prints `PASS screenshots: 0 routes, 79 images`.

Inspect home, polls, night and electorate screenshots at 390×844 and 1280×800, narrow 360px coverage, dark home and actual keyboard focus on a home electorate row. Follow `REVIEW.md`: bugs, security, compliance, then design; supervisor records two review rounds. Missing tools/captures fail explicitly.

## Build order

- [ ] **H-a PR: feed and polls move.** Add shared seat partials, home joins including social, directory/method modules, countdown, navigation, source-note composition and H5 incumbent amendment. Update route/fragment tests, verifier `home`, explorer browser routes and screenshot naming; add home-row focus. Prove `uv run product/nz_election/pipeline/verify.py home` prints `PASS home`; build prints `PASS build: 79 routes`. Before OG expansion, populated harness prints `PASS screenshots: 79 routes, 219 images`. Inspect images. Stage intended files, run `bin/lint` and `uv run --with pytest pytest -q`; record actual `lint ok (<N> text files)` and pytest summary, then commit.
- [ ] **H-b PR: night, detail order and OG output.** Add night copy, candidate-first details, shared summary metadata, all 79 OG variants and PNG generation, verifier `home-routes`, final count tests and runbook instructions. Prove `uv run product/nz_election/pipeline/verify.py home-routes` prints `PASS home-routes`; run `verify.py all` through `PASS all`, host screenshots through `PASS screenshots: 79 routes, 296 images`, OG-only and coalition browser. Inspect required images. Stage intended files, close with `bin/lint` and `uv run --with pytest pytest -q`; quote actual outputs and commit.

Also run `uv run --with pytest pytest -q product/nz_election` as the product acceptance command. Never substitute expected output for execution results or claim a fixed future pytest count.

## Concerns

- **Deployment does not currently generate OG PNGs.** Repository `.github/workflows/pages.yml:101-129` builds, verifies and uploads without a screenshot step. Host-generated images prove H8 locally but do not survive a fresh Actions build. Workflow edits are outside this brief's authorized files. Record a supervisor-owned deployment prerequisite: authorize and wire the existing `--og-only` command between build and upload, then verify all referenced PNGs exist. Do not declare deployed H8 complete before that integration.
- **Incumbency is unsupported.** Omit the marker and amend H5; `test_no_inferred_incumbents` guards against name-based inference. Changed-boundary pages also cannot honestly name a single current holder; metadata uses explicit comparison wording.
- **Unchanged names are not unchanged boundaries.** East Cape must remain eligible despite its rename. The selection test covers that reviewed exception, excludes changed seats with smaller margins and rejects tied/missing baselines.
- **Home social retention differs from POC policy.** Extract rendering without changing POC stale behavior or publication guards. Test old home aggregates and the existing withheld POC independently.
- **Fold pressure is real.** The new title, countdown and links consume space above the strip. Preserve the 780px source-note check and 44px controls; use compact spacing and source disclosures. If the accepted order cannot meet both, report measured geometry for supervisor resolution, not a weakened assertion.
- **Required code changes include removals and retargeting.** Replace root-as-polls dispatch, the seven-route allowlist, root explorer URLs, direct-child strip assumptions, two-specimen OG loop and root `polls` screenshot filename. Route-set, fragment, parity and image-inventory tests guard these changes.
- **Data availability remains honest.** `export.py` and `publish.py` already own polls, geography, candidates, baseline, enrolment, local polls and social. Preserve atomic families and last-good bytes. Do not turn missing captures, unavailable fields or unknown markets into successful empty data.
- **Freeze limits static countdown freshness.** Existing build/deploy guards can leave the pre-freeze countdown visible during election day. Keep those guards; test countdown arithmetic separately and document that the static page cannot update during the freeze.

## Supervisor decisions (2026-10-17 09:30Z, accepted)

1. Two increments as written: H-a (feed, `/polls/` move, navigation, tests) and H-b (night copy,
   candidates-first detail, per-route OG, screenshots). H-a dispatches on the 18 October share.
2. OG in deployment: H-b is authorized to edit `.github/workflows/pages.yml` to install
   Playwright (Chromium only) and run `screenshots.py --og-only` between build and upload, then
   fail the deploy if any referenced `og/<key>.png` is missing. H8 is not complete until a Pages
   run shows it. The node_modules limit is a host rule; Actions is not bound by it.
3. H5 amended: no incumbent marker; the card shows "Held by {party}, {N} votes in 2023 on the
   original boundaries" and the candidates. `test_no_inferred_incumbents` stands. East Cape is
   eligible (renamed, boundary unchanged per the correspondence file); the selection test pins
   that exception.
4. Fold pressure: measured geometry back to the supervisor, never a weakened source-note or
   target check. If the hero plus strip cannot fit 780 px at 390 wide, the jump list moves
   below the strip.
5. The social module renders the last published home aggregate with its date; the POC's own
   stale and withheld behaviour is untouched. The static countdown cannot update during the
   s197 freeze; the runbook says so.
