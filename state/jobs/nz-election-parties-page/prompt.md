# parties/ page: one section per party (undecided readers before advance voting, 26 Oct)

Page plan: intent/nz-election/pages/parties.md

Read first: `AGENTS.md`, `intent/nz-election/pages/parties.md` (accepted 2026-10-22T06:10Z; it decides what is on the page and in what order), `product/nz_election/snapshots/{leaders,positions,candidates-2026,donations}.json` with their loaders in `pipeline/snapshots.py` and `pipeline/snapshot_views.py`, `data/averages.json` via the existing home and polls code (`pipeline/home.py`, `pipeline/home_charts.py`), `pipeline/vote_page.py` and how `build.py` registers `vote/` (the route set pin at build.py:558, nav labels at :560, route cards, screenshot registry) as the pattern for a new route, `intent/nz-election/design-principles.md` and `look-538.md` (style, applied last), `product/nz_election/tests/screenshots.py`.

Branch: `change/nz-election-parties-page` in `.worktrees/nz-election-parties-page`, from main.

Goal: a new route `/unattended/nz-election/parties/` that answers the plan's five questions per party, in the plan's page order, nothing else. Party picker first (one row of party colour chips linking to `#<party_id>` anchors), then one section per party in current-average order: name and leader portrait (with its licence credit), polling number on the latest average with change since a stated date and a sparkline with the 5% threshold rule and the value labelled at the line end (question 4), dated positions with source link (3), one Policy.nz link (1; fetch the party URLs once into a small sourced snapshot, link only, no policy text), leader and top five list candidates with ranks and the EC party list link (2; show a count only if checked complete against the EC list, else the top five alone), donations over NZD 20,000 this year: count, total and the largest three donors with dates and the EC returns link (5; `document_checked` false rows shown as listed, never excluded). Link parties/ from the header nav and from party names on home and polls/ where a party name already renders. Absent means absent: a missing field drops its line, never a placeholder or "not available". Not shown: ideology scores, endorsements, policy matching, full rosters, seat scenarios, histories.

Graphics (plan): the sparkline beside the 538 polling-averages small multiple and the portrait card beside the NBC midterms candidate card, each screenshotted at the same width.

Contracts that move with this change: the registered route set gains `parties/` (build.py pin, nav, route cards, screenshot registry, route counts in tests and the harness). Tests on main at the base sha must not be weakened; the branch's own tests move with it.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass, including new tests: section order follows the latest average, a party missing a field drops that line (no placeholder text), donation totals equal the sum of that party's rows in donations.json including unchecked rows, every picker chip resolves to an anchor.
- `uv run product/nz_election/pipeline/verify.py all` on a populated build prints `PASS all`.
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` prints PASS with the new route count; name the screenshots of parties/ at 360, 390 and 1280.
- Question test (plan): from the 390x844 screenshot alone, the picker and the first party's polling number are above the fold; after one tap on a party chip, answers 1 to 3 for it are readable; say where each is.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
