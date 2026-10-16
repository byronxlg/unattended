Design-system increment for the NZ election site. Worktree .worktrees/nz-election-design, branch
change/nz-election-design from main. Commit there, do not push. Read AGENTS.md first.

Goal: restyle every existing route to intent/nz-election/design.md (draft 2) and add the tests
that hold the design to its numbers. No new data, no new routes except the OG template, no
display font download. The hotfix PR #16 (verify.py presence checks) is merging in parallel and
touches no web file; do not edit verify.py.

Read first, in this order: intent/nz-election/design.md (all of it; the sections "The home
sentence", "Chart grammar: seat strip", "Source notes", "States", "Budgets and checks" and
"Design-system PR" are the contract), intent/nz-election/spec.md lines 240 to 280 (source-note
component, staleness intervals, accessibility), product/nz_election/web/styles.css and
templates/*.html, pipeline/build.py (strip(), label_lanes(), the state bands and the
source-note rendering), pipeline/electorate_pages.py, pipeline/coalitions.py (default scenario,
assumed_majority), web/coalitions.mjs (existing invalid-input copy; keep its words),
tests/screenshots.py (harness, contrast() and the pairing checks that already exist),
tests/test_build.py and tests/test_electorates.py for the patterns.

Invariants, where each is enforced today, and what must hold:

1. Colour never alone and contrast (spec, accessibility section; today tests/screenshots.py
   TEXT_CONTRAST and BOUNDARY_CONTRAST): every pairing in the two token tables and every party
   fill from config/party-colours.json is enumerated by a test, both modes, text 4.5:1, rules and
   fill outlines 3:1. Every fill has a 1 px ink outline in both modes.
2. The home sentence (new; the allocation and assumed_majority come from the pipeline's default
   scenario, selected=[]): exactly the four forms in design.md, M from assumed_majority, never a
   bloc. A unit test covers majority, no majority, two-way tie, three-way tie and no data. The
   marker label is "{M} for a majority".
3. The strip (build.py strip(), label_lanes()): no text on fills, no white patches, labels in ink
   on paper in a row under the strip (wrap to a second line at most on phone), strip 72 px at 390
   and 120 px at 1280, overhang double-ruled, 1 px ink outlines. The seat table and the equivalent
   data stay.
4. First viewport (new): with the fixture bundle at 360 by 780 and 390 by 844 the bottom edge of
   the home page's source note is above the fold. The harness asserts it and fails with the
   measured number.
5. Source notes (spec line 244; today source-note.html and the aria-describedby pattern): one note
   per numeric group placed as design.md says, every table, SVG and prose number linked by
   aria-describedby to its note's id, dates typed (fieldwork, final, retrieved) and rendered in
   Pacific/Auckland, licence and run links present. A test walks the built routes and asserts
   every aria-describedby target exists and every table and figure has one.
6. States (design.md States): each of the twelve has a treatment with reader-facing words and a
   fixture the harness renders. Band copy comes from design.md; explorer copy stays as
   coalitions.mjs has it. Intervals 3 h, 36 h, 90 s. A stale allocation is never shown as
   current.
7. Budgets (design.md Budgets): CSS under 12,000 bytes raw; the home page with linked CSS, SVG,
   JS and startup JSON under 100,000 bytes gzipped from a real fixture build; the test measures
   the built page, not the templates; the map SVG stays lazy.
8. Accessibility (spec): axe-core vendored under tests/ (not served; add it to the lint exemption
   list only if bin/lint flags its bytes, and say so), zero violations on every route at 390 and
   1280; 44 px controls; focus ring 3 px with the paper gap; details-based phone menu works
   without script; headings form an outline.
9. Identity: favicon SVG (tick in a ruled box) plus 180 and 512 PNGs, manifest.webmanifest, an
   og.html template rendered by the screenshot harness for the home page and one electorate at
   1200 by 630 (the Pages workflow wiring is increment 7's; here only the template and a host
   command).
10. Night tokens behind prefers-color-scheme: dark, one night screenshot of the home page.

Allowed test changes: this is a build job, so existing tests may change where the design changes
what they assert (strip markup, label lanes, copy). List every modified assertion in the report
with the design.md line that required it. Do not weaken contrast, provenance or validation tests.

Codex sandbox cannot launch Chromium: write the harness changes and the fixtures, run the Python
and build tests, and name the host commands you could not run. The supervisor runs them.

Definition of done, run on the host, with expected output:
```text
uv run --with pytest pytest -q product/nz_election/tests            -> all passed, 0 failed (count: 269 plus additions minus any you removed, listed)
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/ds-data && uv run product/nz_election/pipeline/build.py --data /tmp/ds-data --out /tmp/ds-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/ds-data --site /tmp/ds-site  -> PASS all
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots   -> PASS screenshots: 77 routes, N images (states, 360, 390, 1280, night, og)
bin/lint                                                            -> lint ok
```
If the harness flags differ, use the real ones and say so. Report: what changed per route in one
line each, the measured numbers (CSS bytes, home page gzipped bytes, source-note bottom edge at
360 and 390 from your calculation if you could not render), every modified assertion with its
reason, the four command tails, and what you could not run. No emojis, no em dashes.
