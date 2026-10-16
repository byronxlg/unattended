# Plan brief: NZ election M2 (Build stage, plan mode)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
This job writes the M2 plan for the product change `nz-election`. Your sandbox is read-only and
has no network: your final message IS the deliverable. The supervisor copies it verbatim into
intent/nz-election/plan-m2.md, so write one complete markdown document, title on the first line,
nothing before or after it, under 320 lines. Write for an engineer who never saw this
conversation and will implement from the plan alone in a fresh context, in a worktree, with
no network, one increment per PR.

M1 is merged and live (PRs #9, #10, #11): the polls page, allocator, averages, exports, six
routes, the hourly workflow, the orphan `data` branch, `pages.yml` with the pinned data checkout.
Read first, in this order: intent/nz-election/spec.md ("Supervisor resolutions" overrides the
body; M2 is requirements 4, 5, 6, 7, 8, the daily workflow and the geography budget),
intent/nz-election/plan.md (the M1 plan, its supervisor decisions and departures: the M2 plan
builds on what shipped, not on what was planned), intent/nz-election/intent.md,
intent/research/nz-election-data-sources.md (sections 1, 3, 4, 5, 6 and "Access reality"),
then the code as it is: product/nz_election/pipeline/*.py (models, export envelope, build.py
rendering, verify.py check registry, refresh.py and publish.py for the data branch contract),
product/nz_election/web/ (templates, styles.css tokens, allocator.mjs), config/*.json,
fixtures/manifest.json (the capture record shape), tests/ (conftest, screenshots.py, how tests
are organised), .github/workflows/nz-election-hourly.yml and pages.yml, runbook.md, REVIEW.md.
Do not write files, do not run anything that mutates.

## What the plan must contain

1. Fixture captures the supervisor must make before each increment (the sandbox and the
   builds never fetch; the daily workflow ingests committed captures). For each: the exact URL
   (query string included), the file name under fixtures/<family>/, the manifest fields (the
   nine already in manifest.json), the expected size, and what the build does when the capture
   is absent (dated or unavailable display, a named failing test, never zero or fabricated).
   At least: the 2025 general and Māori electorate polygons from the Stats NZ ArcGIS service
   in WGS84 at maxAllowableOffset=0.001 (two requests, the research names the layer); the
   reviewed 2020-to-2025 electorate correspondence (say whether it is a capture or a committed
   reviewed config and who reviews it); the 2023 per-electorate party and candidate votes (EC
   CSV families already captured or new ones; the origin returns 403 so Wayback `id_` raw
   URLs); enrolment by electorate with observation date; the Wikipedia 2026 candidates page
   wikitext at a pinned revision (revids API URL); the Polymarket Gamma events for the slugs in
   research section 5 (one JSON per event slug, observation time recorded). Order the increments
   so the first M2 increment needs no new capture.
2. Coalition explorer (requirement 4): an ES module over the existing allocator.mjs and the
   published averages.json and seats.json; party selection, editable electorate assumptions,
   "Seats needed for a majority" from floor(occupied_house / 2) + 1, overhang and list
   capacity handled; no preselected coalition; what the page shows without JS (the static
   calculated seats, the explorer hidden or inert); state in the URL hash so a configuration
   is linkable; `verify.py coalitions` and its PASS line; the browser test (Playwright is
   installed on the host, not in the sandbox: name the test and its PASS line, mark it as a
   host-run command in the definition of done).
3. Markets (requirement 5): Gamma event JSON parse to `markets.json` with the envelope, the
   contract families (next PM, government membership, seat bands) kept separate, quoted price
   as a percentage, liquidity or volume with its unit, resolution criteria link, observation
   time; the Polymarket attribution and quoted terms line (spec resolution 9); where the panel
   sits on the polls page without converting prices into shares; `verify.py markets` PASS line.
4. Geography (requirement 6, the budget): GeoJSON validation (`test_geojson.py` as the spec
   names it: 64 plus 7 ids, rings closed, finite WGS84, antimeridian), the slug registry
   (`config/electorates.json` or equivalent; stable ids, macron names, ASCII search keys),
   the SVG map built at build time (projection, viewBox, per-feature path with a link and a
   title, no tiles, no runtime library), the directory list and macron-insensitive search as
   a small ES module with the full list rendered without JS, the byte budget for the inlined
   or linked SVG per page and how it is enforced by a test; `verify.py geography` PASS line.
5. Candidates and baselines (requirements 7 and 8): the join rules (EC official names and
   party as the spine; Wikipedia and Wikidata claims attached through explicit reviewed
   mapping files, never surname alone; unresolved conflicts preserved in a review file and
   shown as unresolved); `candidates.json`, `party-lists.json`, `baseline-2023.json` shapes
   with field-level source tags; the 71 electorate pages from one template (what each shows:
   2023 party and candidate votes under the original electorate name, successor notes from the
   correspondence file, enrolment with its observation date, local polls where captured);
   `verify.py candidates` PASS line with the 71 count; the screenshot route count grows from 6
   to at least 8 (electorates index plus one electorate page plus the map) and the plan says
   which, with the image count.
6. Daily workflow `nz-election-daily.yml` at 15:43 UTC plus dispatch: steps, what it ingests
   (committed captures only), what it publishes to the `data` branch beside the hourly bundle
   without racing it (the concurrency group, the non-fast-forward retry already in publish.py,
   the separate file set), status.json fields for the daily family (overdue after 36 hours),
   and the pages.yml change if any.
7. Design: carry the spec's Design section and the M1 decisions (type stack, tokens, counts
   inside figures, voter copy, no meaning by colour alone). For the map: selected state, focus
   ring, touch targets at 390 px, the directory as the accessible equivalent. For the explorer:
   the strip reused, the majority line, live region announcing the total. Party colours still
   have `"evidence": null`; say which capture the supervisor must add before M2 screenshots
   are accepted (spec resolution 13).
8. Verification and test inventory: new test files and function names, target counts per
   increment (targets, not gates), `verify.py all` additions, screenshot command with the new
   route and image counts, `bin/lint`, the host-run commands marked as such.
9. Build order as a checklist (`- [ ] ` items) in increments that each ship as a PR, each
   closing with `bin/lint` and the full test run and naming its proving command and expected
   output line. Suggested: increment 4 coalition explorer and markets parse with a committed
   Gamma capture only if one exists at dispatch (otherwise explorer alone); increment 5
   geography and the electorates index with the map; increment 6 candidates, baselines and
   the 71 pages; increment 7 the daily workflow and the markets panel. Reorder if the files
   say otherwise and say why.
10. `## Concerns`: anything in the spec you cannot implement as written for M2 with the route
    you would take; the page weight of 71 pages plus the map; the Pages build duration growth;
    what in the M1 code must change (not just grow) and the test that guards it.

Decisions already made (do not reopen): no bundler, no runtime libraries, no fonts downloaded,
SVG from simplified GeoJSON with no tiles, labelled old-boundary 2023 results (no re-cut),
window mean averages, fixtures captured by the supervisor, the `data` branch written only by
workflows, the slug registry is committed config, product code reaches main only by PR.
