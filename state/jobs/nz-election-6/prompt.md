# Build brief: nz-election increment 6 (candidates, baselines and 71 electorate pages)

You are the engineer in the unattended lab (read AGENTS.md, then product/nz_election/AGENTS.md).
You are in the worktree `.worktrees/nz-election-6` on branch `change/nz-election-6`, based on
main at 0c66a85 (increment 5, geography and the directory, is merged as 3f95c7a and live). The
branch carries one supervisor commit, 3f49469: the increment 6 inputs. Commit there; never push.
No network in your sandbox; builds and tests are offline.

## Goal

Increment 6 of intent/nz-election/plan-m2.md "Build order": candidates, 2023 baselines, enrolment
and the 71 detail pages (spec requirement 6). Read, in order: plan-m2.md "Before increment 6"
(what each capture is and what its test gates), "Data contracts and family boundaries" (the
candidates.json, party-lists.json, candidate-review.json, baseline-2023.json, enrolment.json and
electorate-polls.json rows, and the family grouping), "Candidates, baselines and electorate pages",
"Design and accessibility", "Verification and test inventory" (test_candidates.py and
test_electorates.py by name), "Build order" and "Supervisor decisions" (decisions override the
body; 5, 6, 7, 8 and 10 bind this increment); spec.md requirement 6 and its Design section; then
the code: pipeline/build.py, export.py (envelope, validators, families), geography.py
(registry, SVG, detail outline), daily_refresh.py, verify.py, web/templates/{base,electorates}.html,
web/electorates.mjs, web/styles.css, tests/test_geography.py, tests/test_contracts.py,
tests/screenshots.py, config/{electorates,routes,sources}.json, fixtures/manifest.json.

## Inputs already on the branch (do not refetch, do not edit)

- `fixtures/ec-2023/candidate-votes-by-voting-place-N.csv` for N in 1..72 except 21 (Māngere):
  the Internet Archive was offline when 21 was fetched; the supervisor adds it when it is back.
  Read each file's schema before parsing: explicit electorate total rows exist; never add totals
  to voting-place rows. Port Waikato (its 2023 contest was deferred to a by-election) must come
  out as distinct from zero votes.
- `fixtures/ec-2026/wayback-electorate-candidates.xlsx` (470 rows incl. header, columns start
  Electorate, Party, ...; parse with bounded zipfile/ElementTree only), `wayback-party-lists.pdf`
  (do not parse; see the config below), `wayback-enrolment-{general,maori}.html`. The four
  non-wayback siblings are 873 to 882 byte Incapsula 403 shells kept as evidence that the direct
  source was unavailable; they are not data.
- `fixtures/wikipedia/candidates-2026.{discovery.json,api.json,wikitext}`: pinned revid 1380178146.
- `fixtures/wikidata/candidacies-2026.sparql.json`: P3602 = Q104843407 candidacies with party,
  electorate and rank qualifiers; statement URIs preserved.
- `fixtures/manifest.json`: 110 entries (was 27; `test_capture_manifest` counts them, update it).
- `config/ec-party-lists-2026.json`: supervisor transcription of the PDF, 17 parties, 443 list
  candidates, ranks contiguous per party, names exactly as printed (SURNAME, Given), each with a
  page/column/line locator and the PDF sha256. Reviewed for rank contiguity and spot-checked
  against the layout text; NOT reviewed for identity against the EC spreadsheet, so list
  capacity stays unchecked (`capacity_checked` false, explorer stays conditional) this increment.
  `pipeline/transcribe_party_lists.py` is the tool that produced it (host-run, reads pdftotext
  output); keep it out of the build and the test suite.

## Deliverables (plan names; choose internal shapes yourself)

`pipeline/{candidates,baseline,enrolment,electorate_polls}.py`; `web/templates/electorate.html`
and the CSS for it; `candidates.json`, `party-lists.json`, `candidate-review.json`,
`baseline-2023.json`, `enrolment.json`, `electorate-polls.json` with CSV siblings in the daily
bundle (families `candidates`, `baseline-2023`, `enrolment`, `electorate-polls`, each validating
and advancing independently; dependencies pinned to the registry and config hashes);
`config/electorate-aliases.json` (EC spreadsheet electorate string to registry id, only where the
NFC-normalised string equals the registry name exactly; anything else stays unmapped and is listed
in your report for the supervisor); the `candidates` and `electorates` entries in verify.py; the
71 detail routes (77 total, `PASS build: 77 routes`) with the index map and directory links
retargeted to them; `tests/test_candidates.py` and `tests/test_electorates.py` with the plan's
named functions (target about 28 cases); screenshots.py extended to the named detail routes
(Wellington North for a changed boundary, Te Tai Tonga for a controlled missing-data state) and
the 77-route baseline with safe filenames for nested routes.

Supplemental joins: `config/candidate-mappings.json` ships EMPTY of reviewed mappings (an empty
list plus schema note). Instead add `pipeline/candidates.py propose-mappings --out <path outside
config>` that writes, for supervisor review only, the EC rows whose NFC name, party and
electorate all agree with exactly one Wikidata statement or Wikipedia box, with the locators. The
build never reads the proposal. Until mappings are reviewed, Wikipedia and Wikidata fields render
as unavailable and `join_status` says so.

## Invariants (name where each is enforced; check your diff against the enforcer)

1. EC is the spine: every candidate row's official name and party come from the spreadsheet;
   no row is created from Wikipedia or Wikidata alone except list-only people from the party-list
   config (electorate_id null). Enforced by `test_official_spine_and_explicit_joins`.
2. No join by surname, similarity or row count; only explicit reviewed identifiers. Same test.
3. Conflicts are preserved with all values and provenance; "Unresolved" shown. `test_conflicts_preserved`.
4. List capacity is unchecked while the party-list review lacks identity review; explorer stays
   conditional. `test_list_capacity_requires_complete_review` and the existing
   `test_unknown_capacity_stays_conditional` must both still pass.
5. Totals never double count; Port Waikato is absent-not-zero; the missing Māngere file yields
   "no candidate baseline" for that electorate and the page still renders.
   `test_no_total_double_count`, `test_port_waikato_not_fabricated`, `test_71_pages_and_missing_data`.
   `test_required_baseline_captures` enumerates all 72 files and fails on absence (it will fail
   in your sandbox on 21; report it as the known gap, do not weaken it).
6. Enrolment values carry their actual observation date and roll basis, null when unknown,
   never zero; a shell page yields unavailable. `test_enrolment_capture_has_observation_date`.
7. Successor comparisons list each old electorate separately and are never summed; missing
   correspondence shows unresolved. `test_original_names_and_successor_comparisons`.
8. Date-only observations validate through an explicit extension of the schema; canonical
   instant validation is not relaxed anywhere. Existing `test_timestamp_canon.py` stays green.
9. Hourly ownership and outputs are unchanged; daily owns the new families (decision 6).

## Definition of done (print the exact lines; the host-run ones you cannot run, say so)

```
uv run product/nz_election/pipeline/verify.py candidates        # PASS candidates: 71 electorates
uv run product/nz_election/pipeline/verify.py electorates       # PASS electorates: 71 pages
uv run product/nz_election/pipeline/verify.py all               # ends PASS all
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
uv run product/nz_election/pipeline/daily_refresh.py --out artifacts/nz-election/data   # PASS refresh: daily bundles
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election   # PASS build: 77 routes
uv run --with pytest pytest -q      # all pass except test_reference_capture_required (host-only) and test_required_baseline_captures (Māngere); report the count, target about 337
bin/lint
uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots   # host-run by the supervisor: PASS screenshots: 77 routes, 154 baseline images
```

## Constraints

- Stdlib Python and plain ES modules; no new dependencies, no bundler, no node_modules.
- Never edit captures, the manifest entries, the party-list config or the registry; if any seems
  wrong, say so in the report with the entry and the reason and build around it.
- Keep AGENTS.md changes to corrections of mistakes you actually made.
- Departures from the plan go in a "Departures" list in your final report with the reason.
- Final report (your last message): what you built, the verification output quoted, departures,
  the unmapped EC electorate strings, the proposal file's row count, and the two expected
  sandbox failures.
