# Build brief: nz-election increment 2 (averages, exports, six-page build, screenshots, pages.yml no-data step)

You are the engineer in the unattended lab (read AGENTS.md, then product/nz_election/AGENTS.md).
You are in the worktree `.worktrees/nz-election-2` on branch `change/nz-election-2`, based on
main at 5a93836, which has increment 1 merged (allocator, parser, fixtures, 171 tests). Commit
there; never push.

## Goal

Increment 2 of intent/nz-election/plan.md "Build order": the published data and the live skeleton.
Averaging and threshold watch; the JSON and CSV contracts with manifest and LICENCES.md; atomic
refresh and publication helpers; `refresh.py --fixtures`; `build.py` rendering the six routes
with the design; `verify.py`; `screenshots.py`; and the `pages.yml` build step in no-data mode
(plan supervisor decision 3) so the skeleton goes live when this merges. No hourly workflow,
no data-branch bootstrap, no `workflow_run` trigger: those are increment 3.

## Read first, in this order

1. intent/nz-election/plan.md: "Averaging", "Published data contracts", "Hourly refresh and
   publication" (only the atomic write and last-good retention parts apply now), "Web build and
   design", "Verification and test inventory", "Build order: Increment 2", "Supervisor decisions"
   (3, 4, 7 bind) and "Increment 1 departures".
2. intent/nz-election/spec.md: "Site and directory layout", "Design", "Provenance and downloads",
   "Accessibility and quality", "Testing and acceptance", "Supervisor resolutions" (all).
3. product/nz_election/pipeline/*.py and web/allocator.mjs as they are: build on them, do not
   rewrite them. The allocator contract and the parser's poll ids are fixed.
4. .github/workflows/pages.yml and bin/blog (how the blog reaches site/; the product build must
   never remove or overwrite blog output).
5. REVIEW.md (how you will be reviewed).

## Constraints

- No network in your sandbox, ever. Every input is a fixture or generated locally. Pipeline tests
  that prove publication (atomic bundle, last-good retained, concurrent publishers, non-fast-forward
  retry, older run cannot replace newer) run against temporary local git repositories under
  tmp_path, never a remote.
- Never edit anything under product/nz_election/fixtures/. Never edit existing tests; add new test
  files or new functions. Exact arithmetic stays (int, Fraction, Decimal; BigInt in JS); no floats
  in any comparison or published number.
- Python 3.12+, stdlib only at runtime. `uv run` scripts carry inline metadata with
  `dependencies = []`, except screenshots.py which is run as
  `uv run --with playwright python product/nz_election/tests/screenshots.py ...`.
- Playwright: the host has Chromium 1243 under ~/Library/Caches/ms-playwright but your sandbox
  may not resolve the playwright package offline. Write screenshots.py to the plan's contract
  anyway (serve site under /unattended/ on loopback, six routes from the route registry, 390x844
  and 1280x800, 12 PNGs plus manifest, link, console, overflow, focus, contrast, no-JS and
  reduced-motion checks, `CHROMIUM_REQUIRED` when the browser is missing, never skip). Try to run
  it; if the package cannot be resolved, paste the error and say so: the supervisor runs it on
  the host and the fresh review judges the images. Do not add a root-suite dependency on it.
- pages.yml: after `bin/blog build` add one step that runs build.py with `--data` pointing at a
  path that does not exist and `--out site/nz-election`; the six pages render honestly with no
  data (see Design below). Change nothing else in the workflow. `pytest.ini` may gain nothing;
  collection roots are already set.
- product/nz_election/AGENTS.md: remove the "Increment 1 departures" section (bookkeeping now
  lives in plan.md); keep the durable rules, add any new durable rule this increment teaches.
  Keep it under a page.
- Do not edit state/, posts/, prompts/, bin/, root tests, or any file outside product/,
  .github/workflows/pages.yml and product/nz_election/AGENTS.md.
- No emojis, no em dashes anywhere, including templates and copy. Comments say why.
- When the plan's wording and existing code or a fixture disagree, follow the code and fixture
  bytes, record the departure in your final message, never stop to ask.

## Design (binding; the fresh review judges screenshots against this)

The spec "Design" section and root AGENTS.md "Design" are the rules. The points that most often
go wrong, from the frontend-design guidance the spec was checked against:

- The hero of the polls page is the proportional seat strip, full width, with party seat counts
  set inside it at 40 px on white inset label areas. No headline number above it, no eyebrow,
  no "dashboard" grid of cards. One memorable element; everything else quiet.
- Visual structure encodes information: the 120-seat base is visibly distinct from appended
  overhang; the majority line is a mark on the strip and a sentence ("Seats needed for a
  majority: 61"), not a card. Dividers and numbering appear only where they mean something.
- Type: `"Arial", "Helvetica Neue", sans-serif` is a deliberate ballot-paper choice and methods
  explains it; the 14/16/20/28/40 scale; tabular numerals wherever numbers align; sentence case
  everywhere; prose under 72 characters a line.
- Palette exactly as the plan lists it: paper, ink, muted, surface, vote-orange as the only
  interaction cue (dark text on it, ink boundary), focus-blue 3 px with white separation. No
  shadows, no rounded card kit, no gradients, no tracked capitals, no middle-dot meta strings,
  no arrows on links, no entrance animation.
- Empty and failure states give direction, not mood. The no-data first build says what this page
  will show and when the first data run is expected, in voter words; it never invents a number
  and never shows a stale strip as current. The placeholder pages (electorates, night, campaign)
  are one honest paragraph each.
- Copy is for a voter: "Seats needed for a majority", "Last poll ended 12 October",
  "Updated 2:17 pm, Friday" with Pacific/Auckland time, fieldwork date separate from retrieval.
  Every number links its inputs through the shared source note; "this project" is never the
  only source cited.
- Quality floor: readable without JS (no JS module is loaded in M1), semantic landmarks, skip
  link, table captions, 44 px targets, visible focus, reduced motion respected, 4.5:1 text and
  3:1 boundaries, works at 390 px with labelled local scrolling for wide tables and no page-wide
  overflow. Look at your own screenshots before finishing and say what you changed because of them.

## Definition of done

Run from the worktree root and paste each command's output in your final message:

1. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   expected: a line `PASS refresh: polls bundle`, outputs labelled as offline verification.
2. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`
   expected: `PASS build: 6 routes`.
3. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   expected: `PASS build: 6 routes` with the honest no-data pages (this is what pages.yml runs).
4. `uv run product/nz_election/pipeline/verify.py all` expected: `PASS polls`, `PASS thresholds`,
   `PASS provenance`, `PASS pipeline`, then `PASS all`.
5. `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
   expected: `PASS screenshots: 6 routes, 12 baseline images`; if playwright cannot be resolved
   offline, paste the error instead.
6. `uv run --with pytest pytest -q` expected: all passed, 0 skipped, count greater than 171
   (plan target adds 26 product tests: average 7, contracts 5, pipeline 8, build 6; counts are
   targets, say which you merged and why).
7. `bin/lint` expected: `lint ok (<N> text files)`. Stage new files first. artifacts/ and
   site/nz-election are build outputs: make sure they are ignored, not committed.
8. `git status --short` expected: empty after your final commit.

Final message under 40 lines: files changed, the eight outputs, what the screenshots made you
change, departures from the plan, open questions for the supervisor.
