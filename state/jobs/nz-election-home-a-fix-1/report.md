# PR #29 fix round 1

Base: `7e27c97`, branch `change/nz-election-home`. No push.
Protected baseline: `bb0690d`. No assertion was dropped or given a larger limit.

## Item 1: seat-strip legend

Changed `product/nz_election/web/styles.css:3`: cap `.label-connector` at 6 px.
The inline connector heights formerly extended 27 px from 6 px above the legend,
so later connectors painted over earlier labels and formed empty boxes. The cap
keeps their borders in the existing gap above both label rows. Seat fills,
majority marker, label positions and client/server markup parity are unchanged.

Added `legend_check` at `product/nz_election/tests/screenshots.py:196`, called
on the home at all three baseline widths. It rejects any positive-area overlap
between a visible label and a segment, majority rule or connector. This adds a
check without weakening the existing strip height, outline or label-row checks.

Visual inspection:
- 360: inspected the pre-fix `artifacts/nz-election/screenshots/home-360x780.png`.
  A vertical connector crossed GRN 15 and empty connector boxes hung into the
  legend. No post-fix image could be generated or inspected.
- 390: no post-fix image could be generated or inspected.
- 1280: no post-fix image could be generated or inspected.

Chromium cannot launch in this sandbox. The actual populated-build harness command:

```sh
uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/fix1/screenshots
```

Exit 1, before rendering any route:

```text
CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed
bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.69916: Permission denied (1100)
```

Full log: `artifacts/nz-election/fix1/screenshots.log`. The expected contract is
79 routes and 219 images; no PASS or visual acceptance is claimed. Host execution
and inspection of the three widths remain required.

## Item 2: electorate directory count

Changed the expressly authorized assertion at
`product/nz_election/tests/screenshots.py:356` to count
`.electorate-directory li[id^="electorate-"]`. The equality remains exactly 71.
Unmatched local-poll entries remain visible and are not treated as electorates.
A stdlib HTML-parser probe over the fresh populated page produced:

```text
PASS directory entries: 71 (78 total list items)
```

## Item 3: budgets follow the explorer

`product/nz_election/tests/test_design.py:101` now applies every original limit
to both `index.html` and `polls/index.html`: CSS below 12,000 bytes, transferred
bytes below 100,000, and transfer plus 45,000 reserved font bytes below 100,000.
Failure messages name the page. Identity assets, explorer dependencies, no maps,
no downloaded fonts, and no served axe checks are retained.

Added two negative cases in `product/nz_election/tests/test_home.py:221`.
Each copies the populated site and appends deterministic incompressible padding
inside a comment in `coalitions.mjs`. Home transfer bytes remain unchanged.
60,000 padding bytes fail `RESERVED_FONT_BUDGET: polls/index.html:`;
130,000 fail `FIRST_VIEW_GZIP_BYTES: polls/index.html:`. Both cases invoke the
actual shared page-budget test, rather than reproducing its assertions.

```sh
uv run --with pytest pytest -q product/nz_election/tests/test_home.py::test_poll_budget_rejects_oversized_dependency product/nz_election/tests/test_design.py::test_real_first_view_budget
```

```text
3 passed in 5.34s
```

Fresh populated build measurements:

```text
index.html: CSS=11975; transferred=12690; with reserved font=57690
polls/index.html: CSS=11975; transferred=31370; with reserved font=76370
```

## Build and repository verification

The old untracked artifacts used an earlier social schema and failed validation
with `INVALID_SOCIAL_FIELDS`. They were not edited. Created a fresh fixture bundle
at `artifacts/nz-election/fix1/data` using `refresh(..., end_date='2026-07-18')`,
`daily_refresh`, and `refresh_social(..., fixture=True, send=fixture_send())`,
all with `now='2026-10-17T01:00:00Z'`, social day `2026-10-16`. These are historical
polls and synthetic social examples, not live data. Fixture preparation printed:

```text
PASS populated fixtures: historical polls, synthetic social; offline verification
```

```sh
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/fix1/data --out site/nz-election --now 2026-10-17T01:00:00Z
```

```text
PASS build: 79 routes
```

```sh
uv run --with pytest pytest -q
```

```text
580 passed in 196.72s (0:03:16)
```

```sh
bin/lint
```

```text
lint ok (420 text files)
```

Remaining acceptance work: run the populated screenshot harness on the host,
confirm `PASS screenshots: 79 routes, 219 images`, and inspect the home legend at
360, 390 and 1280. The sandbox restriction prevents completing that part here.
