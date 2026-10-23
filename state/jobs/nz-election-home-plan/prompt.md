# home: rebuild in question rank from the accepted page plan (M2 v1 due 26 October)

Page plan: intent/nz-election/pages/home.md

Read first: `AGENTS.md`, `intent/nz-election/pages/home.md` (accepted 2026-10-20T14:33Z; it decides what is on the home and in what order, including "Graphics", "Not shown" and "Question test"), `product/nz_election/pipeline/home.py` (`page()` at line 274 assembles today's modules: hero seat bar, latest polls, trend, electorates map, leaders, thresholds, markets), `home_charts.py`, `home_checks.py`, `snapshot_views.py`, `vote_page.py` and `pipeline/snapshots.py` (the voting snapshot from PR #53 has the EC key dates and links), `night.py` and `night_page.py` (the night family, for answer 5), `parties_page.py`, the home tests (`tests/test_home*.py`), `tests/screenshots.py` (HOME_* checks), then `intent/nz-election/design-principles.md` and `look-538.md` (style, applied last).

Branch: `change/nz-election-home-plan` in `.worktrees/nz-election-home-plan`, from main. A parallel job (`nz-election-m3-live`) is building the night transport; it does not touch home, vote, parties or electorate modules. Do not edit `night.py`, `night_page.py`, `xml_parser.py` or the workflows; read the night family only through its existing loader.

Goal: the home answers the plan's five questions in rank order, nothing else.
- At 390x844, above the fold: the date line (answer 3: enrol by 25 Oct, advance voting from 26 Oct, election day 7 Nov, from the voting snapshot, links to vote/ and the EC page; after 25 Oct NZ the enrolment clause reads as same-day enrolment per the snapshot, chosen from the build time so the hourly flips it), then the seat bar with its one-sentence answer (answer 1, plan Graphics 1: 122-seat strip grouped by bloc, heavy 62 marker with a direct label, bloc totals large at each end, overhang shown when the allocator gives it).
- Then answer 2: the trend chart and the dated latest polls as one module, with the change since the previous average annotated on the chart; the small parties read against the 5 percent line (plan Graphics 2). Today's thresholds module folds into this or goes; it does not stay a separate module.
- Then answer 4: the hex map electorate picker with the list beside it (keep the closest-margins list only if it fits the module).
- Not on the home any more: leaders (parties/ has them), markets, the social POC link in the body (keep it reachable from the header or footer nav only if it is already there). Markets keep a home elsewhere: move the module to polls/ below the averages, or to methods/#home-markets if it is already rendered there; say which in last.md. Nothing removed from the site, only from the home.
- Answer 5: from 19:00 NZDT 7 November, when the night family is published, a night summary (national seats, percent of voting places reported, update time, link to night/) replaces the seat bar at the top; chosen from the build time and the family, so no code change on the night. Before that, nothing about it shows.
- Absent means absent: a module whose data is missing is omitted, never a placeholder or "not available" (the existing ABSENT_TEXT gate stays).

Contracts that move with this change: the home module set and order (tests pinning the old order, module ids and the HOME_* harness checks that measure removed modules), the polls/ or methods/ route if markets moves there. Tests on main at the base sha may move only where they pin the module set or order the plan replaces; say each one in last.md with the reason. Nothing weaker: budgets, a11y, provenance, ABSENT_TEXT and chart-text checks keep their thresholds.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass, including new tests: home module order equals the plan's (date line, seat bar, polls, electorates); the enrolment clause flips at 2026-10-26T00:00 NZDT and the night summary replaces the seat bar at 2026-11-07T19:00 NZDT with a published night family (injected clocks); leaders and markets absent from the home and markets present on its new route.
- `uv run product/nz_election/pipeline/verify.py all` on a populated build prints `PASS all`.
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` prints PASS; name the home screenshots at 360, 390 and 1280 for before 26 Oct, after 26 Oct and the night state.
- Question test (plan): from the 390x844 screenshot alone, answers 1 to 3 are readable; say where each is and the words a reader reads.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
