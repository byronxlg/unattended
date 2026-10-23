# electorates/<name>/ pages: rebuilt from the accepted page plan

Page plan: intent/nz-election/pages/electorate.md

Read first: `AGENTS.md`, `intent/nz-election/pages/electorate.md` (accepted 2026-10-20T14:33Z; it decides what is on the page and in what order), `product/nz_election/pipeline/electorate_pages.py` (current pages) and its tests, `pipeline/snapshots.py` loaders for `candidates-2026.json`, `candidate-reconciliation-2026.json`, `boundaries-2025.json`, `hexmap.json`, `policy-links.json`, `history.json`, `port-waikato-2023.json` (PR #54 added boundaries and reconciliation), `pipeline/night_electorates.py` (night family electorate results, for answer 5), `intent/nz-election/design-principles.md` and `look-538.md` (style, applied last), `product/nz_election/tests/screenshots.py`.

Branch: `change/nz-election-electorate-page` in `.worktrees/nz-election-electorate-page`, from main.

Goal: each of the 71 electorate pages answers the plan's questions in rank order, nothing else.
- First screen at 390x844: electorate name, candidate race cards (answer 1: party colour bar, name large, party, list rank where one exists, incumbent tag only where the data says so; EC spelling from the reconciliation), and the one line "Check your enrolled electorate at vote.nz" with the official link (answer 2), with the locator graphic (the electorate's simplified 2025 boundary from boundaries-2025.json on an NZ outline at card size, labelled as a locator not a legal boundary, credit Stats NZ CC BY 4.0).
- Then answer 3: link to Policy.nz for this electorate (link only, no ingestion; drop the line when no link exists).
- Then answer 4: 2023 result as horizontal vote-share bars in party colours with the margin annotated, labelled "2023 boundaries" where the boundary changed; Port Waikato from its snapshot; absent when no comparable record.
- Answer 5 (night): when the night family has results for the electorate, leader, margin and reporting status move to the top; before results, nothing about the night beyond what exists today.
- Not shown: competitiveness ratings from old margins, national polls presented as local, enrolment as turnout. Absent means absent: missing data drops its block, never a placeholder (main's ABSENT_TEXT gate binds).
- Sources and licences go to the Methods-anchored provenance pattern already on main, not open dumps on the page.

Contracts that move with this change: electorate page markup, harness checks keyed to the old electorate layout, page byte budgets if the boundary SVG needs it (state the new numbers and why). Tests on main at the base sha must not be weakened; where an old assertion pins removed content, replace it with an assertion on the new content and list each one in last.md. The branch's own tests move with it.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass (Chromium-only failures from the sandbox named as such), including new tests: first-screen order (cards then the vote.nz line), answer 5 promotes to the top with an injected night results fixture, a missing Policy.nz link or 2023 record drops its block, locator SVG present for all 71 electorates and under a stated byte cap.
- `uv run product/nz_election/pipeline/verify.py all` on a populated build prints `PASS all`.
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` prints PASS; name screenshots of three electorates (one general, one Maori, Port Waikato) at 360, 390 and 1280.
- Question test (plan): from the 390x844 screenshot alone, answers 1 and 2 are readable and 3 is within one scroll; say where each is.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
