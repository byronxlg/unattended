# NZ election M1 implementation plan

## Scope and constraints

Implement the supervisor-resolved M1 scope: polls and seats, threshold watch, downloads, methods with the official 2023 worked example, three placeholder pages, hourly refresh, the `data` branch and Pages integration. Produce six routes and 12 baseline screenshots. No markets, geography, candidates, coalition controls, daily workflow or election-night implementation.

Work in the supplied `change/*` worktree. Commit implementation changes there; never push locally. Builds and deterministic tests never fetch. The supervisor captures source fixtures before implementation. Only the hourly Action fetches Wikipedia. Do not edit `state/`, `posts/`, `prompts/`, existing tests or unrelated files.

Python requires 3.12 or later. Executable pipeline scripts use uv inline metadata with `dependencies = []`. Use stdlib HTTP, JSON, CSV, decimal, fractions, HTML escaping, date handling and subprocess support. No runtime libraries, bundler or downloaded fonts. Pytest is the test dependency; Playwright is needed only for real-browser screenshots. Use installed Node for ES-module parity and installed Chromium for screenshots; missing tools fail explicitly, never silently skip.

## File layout and collection

Create the following files under `product/nz_election/`; brace lists enumerate individual files:

```text
AGENTS.md
runbook.md
pipeline/__init__.py
pipeline/{models,fixtures,poll_parser,average,allocator,export}.py
pipeline/{fetch,refresh,publish,build,verify}.py
fixtures/manifest.json
fixtures/wikipedia/{polls-2026.api.json,polls-2026.wikitext}
fixtures/ec-2023/{party-quotients,party-votes,lists-successful,lists-unsuccessful,winners}.csv
fixtures/{allocator-golden,parser-cases,average-cases}.json
config/{sources,party-map,poll-identities,poll-review,party-colours,routes}.json
tests/conftest.py
tests/{test_allocator,test_poll_parser,test_average,test_contracts}.py
tests/{test_pipeline,test_build,test_workflows}.py
tests/allocator_runner.mjs
tests/screenshots.py
web/allocator.mjs
web/styles.css
web/templates/{base,polls,placeholder,downloads,methods,source-note}.html
```

Generated outputs are not application files on `main`: `product/nz_election/data/` exists on the orphan `data` branch; `site/nz-election/` and screenshot artifacts are disposable build outputs.

Create `.github/workflows/nz-election-hourly.yml`; modify `.github/workflows/pages.yml` and `pytest.ini`. Add a short product-instructions link to root `AGENTS.md`, retaining its size limit. Leave `ci.yml`, `bin/blog`, `bin/lint` and existing `tests/` unchanged.

Preserve `norecursedirs = .* product` and `pythonpath = .` in `pytest.ini`; add `testpaths = tests product/nz_election/tests`. Explicit collection roots include product tests without recursively collecting arbitrary product directories. Do not add `tests/__init__.py` or switch import modes: existing tests import sibling test modules. Product tests import `product.nz_election.pipeline` through namespace packages.

Prove collection with `uv run --with pytest pytest --collect-only -q`: both suites must appear. Existing `test_ci_collects_root_tests` asserts the exclusion text and existing CI command; preserve both. CI's root-test guard already passes because four root test files exist.

Product `AGENTS.md` records offline builds, provenance, atomic publication, reviewed mappings, source-family licences, exact arithmetic, design rules and verification commands. `runbook.md` covers capture replacement, drift review, failed refreshes, missing data, retries, rollback and Pages minutes measurement.

## Supervisor fixture capture gate

Capture raw bytes without editing punctuation or CSV banners. Every capture entry in `fixtures/manifest.json` has exactly `path,url,archive_url,captured_at,sha256,reviewer,revision,licence,notes`; nullable fields remain explicit. `captured_at` is UTC ISO 8601, `sha256` hashes committed bytes, and `reviewer` identifies the actual reviewer. Record the resolved timestamped Wayback URL when used, never an invented archive timestamp.

Required sources and destinations:

| Fixture under `fixtures/` | Exact source URL |
|---|---|
| `wikipedia/polls-2026.api.json` | `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Opinion_polling_for_the_2026_New_Zealand_general_election&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main&format=json&formatversion=2&maxlag=5` |
| `wikipedia/polls-2026.wikitext` | Extract main-slot content from that response; record the pinned URL described below |
| `ec-2023/party-quotients.csv` | `https://electionresults.govt.nz/electionresults_2023/statistics/csv/party-quotients.csv` |
| `ec-2023/party-votes.csv` | `https://electionresults.govt.nz/electionresults_2023/statistics/csv/votes-for-registered-parties-by-electorate.csv` |
| `ec-2023/lists-successful.csv` | `https://electionresults.govt.nz/electionresults_2023/statistics/csv/party-lists-of-successful-registered-parties.csv` |
| `ec-2023/lists-unsuccessful.csv` | `https://electionresults.govt.nz/electionresults_2023/statistics/csv/party-lists-of-unsuccessful-registered-parties.csv` |
| `ec-2023/winners.csv` | `https://electionresults.govt.nz/electionresults_2023/statistics/csv/winning-electorate-candidates.csv` |

The first API response supplies both `revid` and wikitext. Replace `REVISION_ID` with that returned integer in `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&revids=REVISION_ID&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main&format=json&formatversion=2&maxlag=5`, recapture, and store this concrete pinned URL in the manifest. Record `https://en.wikipedia.org/w/index.php?oldid=REVISION_ID` and the page history URL in source metadata. No revision number is supplied by the research; invent none.

The inventory identifies the two statistics party-list CSVs. Verify their actual availability and completeness during capture. If either is absent, the supervisor must supply a reviewed equivalent official capture and update this plan's source record before acceptance. Do not fabricate lists or infer candidate identities from ambiguous names.

Validate the pre-Port Waikato snapshot, full minor-party votes, ranked lists and winner identities. Review explicit candidate joins into golden inputs. Strip banner rows only during parsing, with raw files preserved. Never sum both electorate rows and a national-total row.

Missing captures fail with `MISSING_CAPTURE: <path>`; bad hashes fail with `CAPTURE_HASH_MISMATCH: <path>`; inconsistent historical snapshots fail with `FIXTURE_2023_MISMATCH`. Tests fail, never skip or substitute the spec's summary table. Small synthetic edge cases are explicitly labelled synthetic and cannot stand in for official acceptance.

## Poll parsing and identity

`parse_polls(wikitext: str, revision: str, mapping: dict, identities: dict) -> ParseResult` returns `polls,excluded_rows,diagnostics`. `compare_revisions(previous: list, current: ParseResult, review: dict) -> DriftReport` validates changes before publication.

Implement a bounded wikitext scanner, not a regular expression over the entire page. Track table boundaries, sections, links, templates, reference tags and cell separators outside nested constructs. Recognize the national party-vote table semantically: Date, Pollster, Sample, NAT, LAB, GRN, ACT, NZF, TPM, OPP, Others, Lead. Read `data-sort-value` where present; validate against visible date ranges.

Keep fieldwork start/end, pollster, sample, named-party shares, Others, reference URLs and source-row locator. Preserve reference text/history for auditing; Lead is not an input to averaging. Unknown sample sizes and missing shares are null. Parse percentages using `Decimal`, never binary floats.

Expand reviewed rowspans for metadata and header colspans before checking width. Never propagate a share through an unexplained merged cell. Explicit event rows such as `colspan=11` are classified and counted, not interpreted as polls. Resolve named `<ref>` uses, strip footnote markup from numeric parsing and preserve citation links. Reject unknown numeric templates until a reviewed handler exists.

Select tables by section and semantic header signature, not ordinal position. Explicitly exclude electorate, Māori-roll, preferred-PM, approval and forecast-template sections. Keep diagnostics for exclusions; M1 does not publish an electorate-polls dataset.

`config/party-map.json` contains canonical IDs, labels, exact aliases, table-header aliases, aggregate flags, qualifying-list evidence and reviewer references. Map OPP/TOP only through reviewed aliases; never fuzzy-match new parties. `poll-review.json` records approved exclusions, corrections and removals with reasons and revision bounds.

Stable poll IDs are `poll-` plus a SHA-256 prefix of canonical pollster ID, fieldwork start/end and a reviewed survey discriminator. Exclude revision, shares, row number and mutable reference URLs from the key. `poll-identities.json` preserves IDs when dates or labels are corrected and distinguishes separate surveys sharing dates. Ambiguous collisions fail.

`parse_drift` is a typed exception/error code for unknown headers/parties, invalid dates/shares, unexplained width or merge changes, unclassified national rows, ambiguous duplicates, missing previous polls or unexplained count changes. Valid new rows explain count increases; approved removals explain decreases. Diagnostics report old/new counts, IDs and source locators. A correction retains the previous row version in `history`. Drift rejects the entire proposed poll bundle.

## Averaging

Implement `select_window(polls, end_date)`, `deduplicate(polls, identities)`, `check_vector(polls, mapping, review)`, `mean_vector(polls)`, `trend(polls, dates)` and `threshold_watch(polls, average, assumptions)`.

The inclusive window is `[end_date - 29 days, end_date]`, using fieldwork end and the displayed Pacific/Auckland date. Include all national 2026 rows in history; calculate a dated daily series from the first 2026 observation through the current date. Use one latest corrected version per distinct survey and equal weights.

A coherent vector contains every named party reported anywhere in the selected window explicitly in every included row, plus explicit Others. A reviewed exclusion or source mapping may restore compatibility; publish its reason. Missing never means zero. Do not split Others without evidence.

Convert percentages exactly: if maximum decimal precision is `d`, raw values use `10**d` units per percentage point. For `n` coherent polls, averaged integer shares are sums of raw units and `scale = n * 10**d`; displayed percentage is `shares[party]/scale`. Publish `denominator = sum(shares.values())`, including Others, and retain each input's published total. Do not force rounded polls to total 100 or renormalize them. Pass these exact vote-equivalent integers to allocation, excluding Others from eligibility but retaining its denominator contribution.

Publish `method_version = "window-mean-30d-v1"` and `rounding_policy = "display-only-half-up-1dp"`. Descriptive incomplete averages use per-party `{value,scale,poll_ids}` and explicit coverage, never one apparently coherent vector. Set `coherent=false`, `shares=null`, and withhold seats.

Threshold watch includes every named party in the inclusive 2-7% range in the average or any included poll. Show missing coverage, the 5% line and whether the selected electorate assumption permits qualification below 5%.

The page says why seats are unavailable, identifies missing party/poll combinations, shows descriptive shares and poll history, and links the method. It does not show an old seat strip as the current calculation.

## Allocator contract

Implement the same pure contract in `pipeline/allocator.py` and `web/allocator.mjs`:

```text
allocate({partyVotes,electorateWins,lists,electorateWinners,nonListWinners,
          baseSeats:120,tieOrder})
 -> {entitlements,listMembers,seats,overhang,vacancies,occupiedHouse,
     quotients,unresolvedTies}
```

Use Python integers/Fraction and JS BigInt cross-products. Shared JSON stores large integer inputs as decimal strings; adapters validate and convert them. Return JSON-safe exact numerator/divisor strings for quotients. Reject negatives, booleans, inconsistent counts, duplicate people, non-integers, invalid base seats and impossible candidate capacities.

Qualify listed parties at `100 * votes >= 5 * total_valid_votes`, or through an electorate win. Include excluded-party and Others votes in the denominator. Award the highest `baseSeats - len(nonListWinners)` odd-divisor quotients. Validate electorate winners against supplied candidate IDs and counts.

Retain electorate wins; list entitlement is `max(entitlement - electorateWins, 0)`. Skip electorate winners while filling ordered lists. Exhaustion produces vacancies, never redistribution. `occupiedHouse = baseSeats + overhang - vacancies`; majority is `occupiedHouse // 2 + 1`.

`tieOrder` contains recorded lot order and its evidence reference. A tie crossing the allocation boundary without evidence returns boundary details in `unresolvedTies` and null definitive totals. Never resolve it alphabetically or randomly. Zero total valid votes is invalid; individual zero-vote parties remain valid inputs.

Official golden acceptance: 2,851,211 valid votes; entitlements NAT 48, LAB 34, GRN 15, ACT 11, NZF 8, TPM 4; electorate counts 43,17,3,2,0,6; occupied seats 48,34,15,11,8,6; two overhang seats; House 122. Compare all 120 winning exact fractions and ordering to the captured quotient CSV, allowing only documented CSV display rounding. Last winner: `330907/29`; highest loser: `1085851/97`.

For current polls, reuse the exact entitlement/overhang primitive in both implementations. Verified 2026 capacity is unavailable: publish theoretical seats with `capacity_checked=false`, null `list_members`, `vacancies`, `occupied_house` and definitive majority; expose separately labelled `assumed_house` and `assumed_majority` assuming sufficient lists. Do not manufacture candidates to call the full allocator. Label “List capacity not checked” and “2023 electorate seats assumed; 2026 has different boundaries”. Unassigned electorates remain unprojected.

`fixtures/allocator-golden.json` holds reviewed official normalized inputs and expected results plus labelled synthetic edge cases. `tests/allocator_runner.mjs` reads the same file and writes canonical output. Python/JS parity compares full results, including ties and validation failures; the test fails `NODE_REQUIRED_FOR_PARITY` if Node is absent. M1 pages load no JS; the allocator module is shipped for the required parity contract and later interaction.

## Published data contracts

Every JSON envelope has exactly `schema_version,source,fetched_at,run_url,code_sha,data`; derived files additionally have `input_hashes,method_version,generated_at`. `schema_version=1`. Source entries have `id,url,revision,licence,fetched_at,history_url`; nullable revision/history are explicit. Mixed-source acquisitions retain their individual times; envelope `fetched_at` is the latest input acquisition, never build time.

All data rows include `id,source_ref,observed_at`. `source_ref` contains source IDs and revision/row locators; `observed_at` is the observation date or operational event time. Retained bundle bytes retain their original run, code SHA and acquisition times. Operational records without acquired inputs use null `fetched_at`.

| File | Additional exact payload keys |
|---|---|
| `polls.json` | Array: `fieldwork_start,fieldwork_end,pollster,sample,shares,scale,reference_urls,revision,history`; history entries: `revision,source_ref,fieldwork_start,fieldwork_end,shares,scale,reference_urls` |
| `averages.json` | Array: `date,window_start,window_end,coherent,shares,scale,denominator,descriptive,poll_ids,excluded_ids,exclusions,missing,rounding_policy`; exclusions: `poll_id,reason,review_ref`; missing: `poll_id,party_id` |
| `seats.json` | Object: `average_id,available,reason,assumptions,entitlements,list_members,seats,overhang,vacancies,occupied_house,majority,assumed_house,assumed_majority,capacity_checked,quotients,unresolved_ties` |
| `status.json` | Array: `dataset,state,last_attempt_at,last_success_at,last_good_run_url,error_code,message`; state is `fresh`, `stale` or `unavailable` |
| `manifest.json` | Array: `path,format,sha256,bytes,row_count,licences,observation_start,observation_end,fetched_at,producing_run_url,input_hashes` |

`assumptions` has `electorate_wins,non_list_winners,unassigned_electorates,base_seats,basis,capacity_policy,source_ref`; basis is the reviewed pre-Port Waikato 2023 fixture. Quotients have `rank,party_id,numerator,divisor,selected`; unresolved ties have `rank,places_remaining,candidates,tie_order_ref`.

Each JSON has a same-basename CSV, including status and manifest. CSV columns repeat `schema_version,source_json,fetched_at,run_url,code_sha,input_hashes_json,method_version,generated_at` followed by payload keys. Flatten arrays of records to rows; preserve nested collections in documented canonical `*_json` columns, never discard members. Empty unavailable datasets are not published as successful datasets.

`manifest.json` and `manifest.csv` describe identical entries. Include both manifest paths but set their hashes and sizes null, with the documented reason “self-reference excluded”; hash every other published file, including `LICENCES.md`. Counts mean payload records; a seats object counts as one. Immutable download URLs use the checked-out data commit SHA supplied at build time, avoiding a self-referential commit SHA inside its own manifest.

`LICENCES.md` separates Wikipedia-derived polls, averages and seats under CC BY-SA 4.0 from EC-derived validation material. Preserve contributor-history and revision links. EC line: “Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.” Legislation line identifies sections 191-193 and no copyright. Publish only normalized EC data, never PDF/XLSX reproductions.

## Hourly refresh and publication

Workflow name: `NZ election hourly`. Triggers: cron `'17 * * * *'` and `workflow_dispatch`. Trusted branch: `main`. One serial refresh job followed by one publication job. Refresh has read permission; publication alone has `contents: write`.

1. Check out triggering main commit, set up uv, record `GITHUB_SHA` and Action run URL, and read the existing data snapshot if present.
2. Fetch Wikipedia API revision/content serially with the specified User-Agent, `maxlag=5`, 20-second request timeout, 2 MiB response limit and at most three attempts. Honor `Retry-After` and applicable crawl delays; excessive delays become a handled failure. Never fetch linked news sources.
3. Validate revision, parse, compare previous rows, average and calculate in a temporary staging directory. Polls, averages, seats and their CSVs form one atomic bundle. Unchanged source acquisition can update fetch status without pretending a new poll occurred.
4. Catch expected HTTP, validation and `parse_drift` failures. Retain all last-good bundle bytes; produce new status and manifest. With no previous bundle, publish operational files only, state `unavailable`.
5. Upload staged validated outputs and a typed result record. Handled failure does not prevent publication; unexpected process failure blocks unvalidated publication.
6. Publication job uses concurrency group `nz-election-data-publication`, `cancel-in-progress: false`, shared with the future daily writer. Fetch the current tip immediately before applying owned files.
7. If `refs/heads/data` is absent, initialize a temporary orphan checkout and commit only `product/nz_election/data/`. Never copy main's tree, execute data-branch files or bootstrap from a machine.
8. Apply only the validated poll bundle and its own status entry; merge other entries and regenerate the combined manifest. Stage explicit owned paths, not `git add .`. Skip a byte-identical commit.
9. Push without force. On non-fast-forward, fetch the new tip, reapply owned changes and regenerate the manifest; retry at most three times. Do not overwrite a newer successful poll acquisition with an older run's bundle or status. Exhaustion fails visibly.
10. Add Action summary with dataset state, error code, safe diagnostic, attempted revision, last-good acquisition/run, committed data SHA and retry outcome. A final reporting step may fail the workflow after a handled refresh failure has been published; `workflow_run` therefore must not require success.

`publish.py` supports a local bare-repository test transport, with no GitHub calls in tests. Treat fetched paths as data: reject symlinks, traversal, unknown schema and non-allowlisted filenames. Status publication cannot be guaranteed after runner termination or GitHub write failure; the failed Action summary is the fallback.

## Pages workflow change

Retain `main` push and manual dispatch. Add `workflow_run: {workflows: ["NZ election hourly"], types: [completed], branches: [main]}`. Check triggering repository/branch; do not execute workflow artifacts or code from the data branch. A token-authenticated data push is not the deployment trigger.

Change existing concurrency group `pages` to `cancel-in-progress: false`. All push, dispatch and workflow-run deployments share it; pending builds may coalesce while an active deployment completes.

Keep the first main checkout with `fetch-depth: 0`. Keep `bin/blog check`, literal `bin/metrics` with its current `GH_TOKEN`, and literal `bin/blog build`. Resolve the data ref read-only, then perform a second checkout of that exact SHA into `_nz-election-data/`. An absent ref is a supported first-deploy state; authentication/network errors are failures, not absence.

After metrics and before `bin/blog build`, run `uv run product/nz_election/pipeline/build.py --data _nz-election-data/product/nz_election/data --out site/nz-election`, then product validation. Without a data ref, pass a nonexistent data path and render six honest “No data yet” pages, retaining the fixture-backed methods example. Do not substitute fixture polls as current production data.

Write `site/nz-election/build-manifest.json` and its CSV sibling with envelope plus `id,source_ref,observed_at,code_sha,data_sha,build_run_url,built_at,data_available`; `data_sha` is null on first deploy. Add these build records to the rendered downloads catalogue separately from the immutable data manifest.

Preserve upload-pages-artifact and deployment permissions/environment. Any product integrity failure blocks upload/deployment, keeping the previous Pages deployment live. Expose manual dispatch inputs for trusted pinned code/data SHAs for rollback; validate them and record the actual checked-out SHAs.

## Web build and design

`build.py` reads validated local data, escapes all source text, allows only safe HTTP(S) citation URLs, renders templates with a small stdlib placeholder renderer, copies assets/data and writes only beneath its resolved output directory. No template execution, bundler or network. Print `PASS build: 6 routes`.

Generate `/unattended/nz-election/`, `electorates/`, `night/`, `campaign/`, `downloads/`, `methods/`, each as `index.html`. The three placeholders contain one paragraph explaining the later feature without invented data. Downloads uses the manifest inventory; methods gives the 2023 worked calculation, window method, exact arithmetic, assumptions and licences. Navigation uses the spec's labels.

Use `paper #FFFFFF`, `ink #181818`, `muted #595959`, `surface #F0F2F4`, `vote-orange #F58220`, `focus-blue #005EA8`. Party colours: NAT `#00529F`, LAB `#D82C20`, GRN `#098137`, ACT `#FDE401`, NZF `#000000`, TPM `#B2001A`, OPP `#6B3FA0`, each with `evidence:null`. Other parties use named neutral patterns.

Use `"Arial", "Helvetica Neue", sans-serif`; explain the ballot-paper and no-download rationale on methods. Type sizes: 14/16/20/28/40px; prose line-height 1.5, large labels 1.15; tabular numerals for aligned numbers. Gutters 16px mobile/32px desktop, 8px spacing increments, maximum width 1120px, prose under 72 characters, two columns at 800px.

The proportional strip is the hero above history; party counts sit inside it at 40px. Put ink text on white inset label areas within party segments, preserving proportional coloured area and accessible boundaries. At phone widths, small segments use anchored label lanes within the strip figure rather than squeezed or overlapping text. Distinguish the 120-seat base and appended overhang. Show names, counts and a corresponding table; never rely on colour.

Use sentence-case voter copy, including “Seats needed for a majority”, “Last poll ended …” and “Updated …”. Capacity-dependent majority is explicitly conditional. No headline number above the strip, cards, shadows, decorative rules, tracked capitals or entrance animation.

The shared source-note links original revision, contributing rows/calculation inputs, method, licence and producing run. Show fieldwork date separately from retrieval time, formatted with `Pacific/Auckland` and NZST/NZDT. Carry the spec's P and A attribution; explanatory prose never uses “this project” as the sole source.

All content is readable without JS; no interactive seat-strip module is loaded in M1. Use semantic landmarks, skip link, table captions, 44px targets, 3px blue focus with white separation, reduced-motion support, 4.5:1 normal text and 3:1 meaningful boundaries. Wide tables have labelled local scrolling; no page-wide overflow.

## Verification and test inventory

Implement 54 product test functions, with case loops inside tests where needed; no network or browser dependency in the root suite:

- `test_allocator.py` (14): `test_2023_official_result`, `test_all_120_quotients`, `test_exactly_five_percent`, `test_below_five_with_electorate`, `test_below_five_without_electorate`, `test_excluded_votes_in_denominator`, `test_independent_and_unlisted_winners`, `test_multiple_overhang_parties`, `test_exhausted_lists`, `test_electorate_winners_skipped`, `test_cutoff_ties`, `test_zero_votes_and_invalid_inputs`, `test_scaled_equivalent_inputs`, `test_python_js_parity`.
- `test_poll_parser.py` (10): `test_pinned_wikitext`, `test_event_rows`, `test_footnotes_and_named_refs`, `test_merged_cells`, `test_changed_headers`, `test_malformed_rows`, `test_non_national_tables_excluded`, `test_stable_ids_and_corrections`, `test_unknown_party_mapping`, `test_unexplained_row_count_drift`.
- `test_average.py` (7): `test_inclusive_window`, `test_corrected_poll_deduplication`, `test_coherent_vector`, `test_missing_is_not_zero`, `test_exact_integer_mean`, `test_trend_dates_and_rounding`, `test_threshold_membership`.
- `test_contracts.py` (5): `test_capture_manifest`, `test_envelopes_and_provenance`, `test_csv_round_trip`, `test_manifest_hashes_and_licences`, `test_official_candidate_identity_joins`.
- `test_pipeline.py` (8): `test_atomic_poll_bundle`, `test_last_good_retained`, `test_first_failure_unavailable`, `test_partial_failure_preserves_unowned_files`, `test_retry_after_and_timeouts`, `test_concurrent_publishers`, `test_non_fast_forward_retry`, `test_older_run_cannot_replace_newer_data`.
- `test_build.py` (6): `test_six_routes_and_prefix`, `test_no_data_first_build`, `test_incomplete_vector_withholds_seats`, `test_source_html_escaped`, `test_build_preserves_blog`, `test_failed_validation_preserves_deployment`.
- `test_workflows.py` (4): `test_hourly_contract`, `test_orphan_bootstrap`, `test_pages_triggers_and_pinned_checkouts`, `test_status_published_after_handled_failure`.

`verify.py polls|thresholds|provenance|pipeline` runs deterministic fixture-backed checks and prints exactly `PASS polls`, `PASS thresholds`, `PASS provenance`, `PASS pipeline` respectively. Accept optional `--data` and `--site` to additionally validate real outputs. `all` runs those four M1 checks then prints `PASS all`; do not imply M2-M4 checks passed.

Checks cover history coverage/vector withholding/strip order; inclusive threshold membership and electorate labels; row-to-input links, CSV parity, hashes and licences; and atomic failure, absent data, concurrent writers, retries and failed-deployment retention. Verification may create disposable temporary outputs but must never fetch.

`uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots` serves the supplied site beneath `/unattended/` on loopback. Discover exactly six product routes from the route registry and generated files; visit all at 390x844 and 1280x800 using installed Chromium. A missing browser fails `CHROMIUM_REQUIRED`; only CI may install Chromium.

Write 12 route/viewport-labelled PNGs and a manifest containing route, viewport, path, hash, code/data SHAs and browser version. Check local links, console errors, overflow, keyboard focus, actual contrast pairs, JS-disabled rendering and reduced motion. External citation links are not fetched. Print `PASS screenshots: 6 routes, 12 baseline images`; extra unavailable, stale and incomplete-vector images are listed separately. Inspect every baseline image before review.

`bin/lint` must retain `lint ok (<N> text files)`. Stage intended new files before this tracked-file check. Quote real pytest counts and command outputs in implementation reviews; the counts here are targets, not observed results. Review in `REVIEW.md` order: bugs, security, compliance.

## Build order

### Increment 1: fixtures, parser and allocator, no UI

- [ ] Commit supervisor captures, manifests, reviewed mappings, parser, Python/JS allocator and shared golden inputs. Prove with `uv run --with pytest pytest -q product/nz_election/tests/test_allocator.py product/nz_election/tests/test_poll_parser.py`; expected summary contains `24 passed`.
- [ ] Add explicit pytest collection roots and product instructions. Prove with `uv run --with pytest pytest --collect-only -q`; expected output includes both `tests/` and `product/nz_election/tests/` node IDs.
- [ ] Finish the PR with `bin/lint` and `uv run --with pytest pytest -q`; expect `lint ok (<N> text files)` and a passing summary for existing tests plus 24 product tests. Commit, obtain fresh review and let the supervisor merge.

### Increment 2: outputs and six-page build

- [ ] Implement averages, schemas, CSVs, atomic refresh/publication helpers and tests. Provide offline CLI `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`; expect `PASS refresh: polls bundle`. Fixture runs are visibly labelled offline verification, never production.
- [ ] Implement templates, design, methods example and first-deploy fallback. Run `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`; expect `PASS build: 6 routes`. Run `uv run product/nz_election/pipeline/verify.py all`; expect the four check lines followed by `PASS all`.
- [ ] Run the screenshot command above, inspect 12 baseline images and extra failure states; expect `PASS screenshots: 6 routes, 12 baseline images`.
- [ ] Finish the PR with `bin/lint` and `uv run --with pytest pytest -q`; expect the lint contract and a passing summary including 50 product tests. Commit and obtain fresh review.

### Increment 3: Actions and branch bootstrap

- [ ] Add the hourly workflow, Pages diff, workflow tests and operational runbook. Run `uv run --with pytest pytest -q product/nz_election/tests/test_workflows.py`; expect `4 passed`. Run `uv run product/nz_election/pipeline/verify.py pipeline`; expect `PASS pipeline`.
- [ ] Prove product-before-blog preservation with `uv run --with pytest pytest -q product/nz_election/tests/test_build.py`; expect `6 passed`. Run the screenshot command after the combined site build; expect `PASS screenshots: 6 routes, 12 baseline images`.
- [ ] Finish the PR with `bin/lint` and `uv run --with pytest pytest -q`; expect the lint contract and a passing summary including all 54 product tests. Commit and obtain fresh review.
- [ ] After merge, the supervisor verifies an initial no-data Pages deployment, dispatches `NZ election hourly`, and checks orphan creation, status publication and the subsequent Pages run. Run `verify.py all --data <data-checkout>/product/nz_election/data --site site` against downloaded/check-out artifacts; expect `PASS all`. Record actual Actions URLs, data/code SHAs and deployed screenshots before closing M1.

## Concerns

- The supplied research contains no numeric Wikipedia revision or captured official bytes. Fixture capture is a hard build prerequisite. Exact candidate joins and CSV schema must be reviewed against those bytes; acceptance cannot be based on the six-party summary alone.
- Full s193 current-poll results cannot be claimed without 2026 list capacity. Publish conditional entitlement/overhang seats and assumed majority, with actual vacancies/occupied House unknown. Full s191-193 behavior remains proven on the official 2023 fixture and synthetic edges.
- The supervisor's counts-inside-strip direction overrides the body's external-label preference. Use white inset labels and anchored lanes within the figure; screenshots must prove small-party labels fit at 390px without changing proportions.
- Existing root tests lock pytest's product exclusion. Explicit `testpaths` is the compatibility route; prove collection before proceeding. Do not weaken that existing assertion.
- `bin/blog build` currently preserves `site/nz-election/`, but writes root index, feed, about, posts, metrics and `.nojekyll`; product output must never target those paths. `bin/metrics` owns `site/data/metrics.json`, distinct from product data. Preserve workflow ordering and literal commands required by existing integration tests.
- A handled source failure can publish status; runner loss, denied writes or failed Pages deployment cannot update the public site. Show overdue state after three hours based on last success at build time, and disclose the page build time. With no runtime JS, a loaded page's age label does not update itself.
- M1 has up to 24 scheduled Pages builds/day, approximately 720 per 30 days, plus pushes/manual runs. At 1-3 billed minutes/build that is roughly 720-2,160 Pages build minutes/month; hourly refresh/publication costs are additional. Coalescing reduces duplicates, not the hourly baseline. Record actual duration and account billing for several days; do not assert available quota or silently reduce cadence.
- Offline uv execution requires cached Python/test packages, Node and Chromium. Missing prerequisites are explicit environment failures. This planning run only read repository files; no tests, captures, builds or deployments are claimed verified.