# NZ election design-system report

Implemented against `intent/nz-election/design.md` draft 2. The worktree started before draft 2
and PR #16; rebased onto upstream `9694410` after both became available. No task changes to
`verify.py`, data captures, routes, workflows or state files. No display font or runtime dependency.

## Verification and measurements

- Python: 269 upstream tests plus 18 additions, zero removed. One strip test renamed for the new grammar.
- CSS: 10,609 raw bytes, below 12,000. The build no longer appends 71 map selectors.
- Default fixture home (including linked identity assets): 17,478 gzipped bytes, measured from built HTML and its dependencies.
- Coherent fixture home, including both startup JSON files: 30,685 gzipped bytes. With 45,000 font bytes reserved: 75,685, below 100,000.
- Default fixture source-note bottom: approximately 456.8 px at 360 and 390. Coherent allocation: approximately 670.8 px at both widths.
- These are calculations, not screenshots: Helvetica Neue regular/bold system font metrics, word wrapping, 44 px inline links, CSS line heights and collapsed block margins. Actual browser shaping and line boxes can differ. The harness measures and reports actual positions and fails above 780 px at either phone width.
- Map remains absent from the home transfer. Electorate-page SVG total remains exactly 286,336 bytes including favicon; the map itself is 286,132 bytes.
- axe-core 4.10.3 is vendored under tests only, with licence, source and checksum in `tests/axe-NOTICE.md`. Lint did not flag its bytes; no exemption added.

Transfer inventory: gzip per text resource; the linked PNG uses its existing compressed bytes.

```json
{
  "default": {
    "index.html": 6777,
    "coalitions.mjs": 4447,
    "allocator.mjs": 2240,
    "styles.css": 2861,
    "manifest.webmanifest": 218,
    "icon-180.png": 773,
    "favicon.svg": 162
  },
  "coherent": {
    "index.html": 8130,
    "coalitions.mjs": 4447,
    "allocator.mjs": 2240,
    "data/seats.json": 2324,
    "data/averages.json": 9530,
    "styles.css": 2861,
    "manifest.webmanifest": 218,
    "icon-180.png": 773,
    "favicon.svg": 162
  }
}
```

## Commands and tails

```text
uv run --with pytest pytest -q product/nz_election/tests
287 passed in 144.42s (0:02:24)

uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/ds-data && uv run product/nz_election/pipeline/build.py --data /tmp/ds-data --out /tmp/ds-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/ds-data --site /tmp/ds-site
PASS refresh: polls bundle
PASS build: 77 routes
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS all

uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
NOT RUN: Chromium cannot launch in this sandbox, as specified in the task.

bin/lint
lint ok (313 text files)
```

The harness flags are the requested `--site` and `--out`. Its inline uv metadata installs Playwright;
Chromium must already be installed on the host. All browser checks remain pending: axe, actual
contrast/targets/focus, no-script menu, viewport measurements, screenshots and five-second visual review.
No browser results or screenshot counts are claimed. The harness reports its actual image count.

The baseline covers all 77 routes at 390x844 and 1280x800, plus eight representative routes at
360x780, sixteen state variants covering all twelve specified categories, a coherent 360 fixture,
all 71 directory names, a night home image, and two OG images. Missing published map or baseline
data is explicitly asserted as missing, rather than requiring unprovided families.
For the full map baseline, run the existing daily fixture ingestion before rebuilding:

```sh
uv run product/nz_election/pipeline/daily_refresh.py --out /tmp/ds-data
uv run product/nz_election/pipeline/build.py --data /tmp/ds-data --out /tmp/ds-site/nz-election
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots-full
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-og --og-only
```

The OG-only command renders home and Wellington North at 1200x630. The electorate OG fixture
uses the existing captured boundary when the supplied site is polls-only. No Pages wiring added.

## Every changed existing assertion

Line numbers below refer to draft 2 now present in this branch.

| Test | Changed assertion and reason | design.md |
|---|---|---|
| test_build: 77 routes | CSS contains 26px instead of 40px; phone sentence uses the specified scale | 95-96 |
| test_build: no data | Old promised publication date replaced with `Polls are checked hourly.`; no-strip, official example and absent data SHA checks retained | 224-226 |
| test_coalitions: static content | Exact figure checked separately from retained seat table because the note now intervenes; fallback and provenance checks retained | 206 |
| test_electorates: missing data | Added exact `No 2023 candidate results for this electorate` summary; retained original diagnostic and original-result assertions | 249-250 |
| test_generation_provenance: observation dates | Require typed datetime containing UTC and visible Auckland date; still prohibit visible UTC and preserve exact raw record and immutable manifest | 211-213 |
| test_geography: SVG bytes | Exact 286,091-byte total becomes 286,132-byte map plus 204-byte favicon, 286,336 total; source description and currentColor add 41 map bytes | 180-181, 211-213, 268-269 |
| strip regression: label party set | Four small-party labels replaced with all six fixture parties in descending seat order; counts and abbreviations checked | 165-169 |
| strip regression: spatial anchors | Midpoint anchor, leader and elbow class assertions replaced with external labels after the strip and empty fill contents; compact connectors originate at segment starts | 166-171 |
| strip regression: mobile rows | More-than-one staggered lane becomes exactly two rows for the crowded fixture and one on desktop | 168-170 |
| strip regression: type and CSS exclusions | 40px/anchor CSS and bans on grid/small-lane rules replaced with 26/32 title scale, 72/120 strip heights and 1px outlines | 95-96, 108-112, 163-170 |
| strip regression: crowding helper | Three lanes for three crowded anchors replaced with at most two phone rows for six labels | 168-170 |
| screenshots: boundary contrast | Same 3:1 minimum measured against computed paper instead of hardcoded white, so dark mode is checked | 289-290 |
| screenshots: target size | Existing 44px link check extended to summaries, buttons and inputs | 286-288 |
| screenshots: strip states | Retained visibility checks expanded to rejection fixtures; removed `.seat-label` selector because that markup no longer exists; all external labels checked for overflow | 165-171, 240-243 |
| screenshots: map presence | Assert map count equals supplied geography presence, and explicit missing copy otherwise; layer/focus checks still mandatory when geography exists | 234-235, 246-250 |
| screenshots: Wellington baseline | Original-name assertion retained when baseline is supplied; explicit unavailable baseline required otherwise | 234-235, 246-250 |

No contrast threshold, provenance guarantee, input-validation rule, script allowlist or test was removed.
After expanding transfer accounting to include linked identity assets, the 18 design tests also passed in 20.00s.

New checks cover exact sentence forms (including three-way tie and absent data), default unselected
scenario, both token sets and every party fill, actual built budgets, source-target integrity for
published and absent routes, typed dates, icons, stale allocations, interval boundaries and state fixtures.
The 14/21 external label rule at lines 166-170 takes precedence over the conflicting 32/48 strip-number
scale at line 96, because two display-sized label rows cannot fit the mandatory 42 px label budget.

## Route changes

- `/`: Exact calculated-seat sentence, compact strip/labels, source before seat table, dated poll evidence and honest state bands.
- `/electorates/`: Neutral map outlines, selection treatment, phone directory, unmatched local polls and described boundary source.
- `/night/`: Shared ballot typography, navigation, focus and dark tokens; existing planned-view copy retained.
- `/campaign/`: Shared ballot typography, navigation, focus and dark tokens; existing planned-view copy retained.
- `/downloads/`: Ledger rows, typed observation dates, source link and fixture-run label; original records retained.
- `/methods/`: Ledger typography and table, programmatic numeric source references, dated Electoral Commission validation note.
- `/electorates/auckland-central/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/banks-peninsula/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/botany/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/christchurch-central/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/christchurch-east/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/coromandel/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/dunedin/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/east-cape/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/east-coast-bays/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/epsom/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/glendene/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/hamilton-east/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/hamilton-west/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/henderson/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/hutt-south/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/ilam/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/invercargill/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/kaikoura/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/kaipara-ki-mahurangi/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/kapiti/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/kenepuru/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/mangere/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/manurewa/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/maungakiekie/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/mt-albert/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/mt-maunganui/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/mt-roskill/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/napier/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/nelson/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/new-plymouth/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/north-shore/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/northcote/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/northland/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/otahuhu/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/pakuranga/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/palmerston-north/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/papakura/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/port-waikato/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/rangitata/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/rangitikei/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/remutaka/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/rotorua/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/selwyn/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/southland/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/taieri/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/takanini/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/tamaki/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/taranaki-king-country/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/taupo/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/tauranga/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/tukituki/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/upper-harbour/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/waikato/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/waimakariri/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/wairarapa/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/waitakere/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/waitaki/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/wellington-bays/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/wellington-north/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/west-coast-tasman/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/whanganui/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/whangaparaoa/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/whangarei/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/wigram/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/hauraki-waikato/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/ikaroa-rawhiti/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/tamaki-makaurau/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/te-tai-hauauru/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/te-tai-tokerau/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/te-tai-tonga/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.
- `/electorates/waiariki/`: Shared light/night ledger, neutral outline, linked numeric sources, typed dates and explicit missing-result disclosure.

## Remaining review

Host browser execution and visual review are required before declaring the UI verified. No screenshots
were produced or inspected in the sandbox. No unresolved data or allocation questions were introduced.
The 77 existing routes remain; `og.html` is a harness template, not a new published data route.
