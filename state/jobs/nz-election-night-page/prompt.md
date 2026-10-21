# night/ page: election night results and the replay rehearsal

Page plan: intent/nz-election/pages/night.md

Read first: `AGENTS.md`, `intent/nz-election/pages/night.md` (accepted 2026-10-20T14:33Z; it decides what is on the page and in what order), `intent/nz-election/plan-m3.md` increment 2 (the page half: `pipeline/night_page.py`, `web/night.mjs`, `web/night-parser.mjs`, night template, `tests/night_browser.py`, screenshot states) and "Existing contracts and common verification", the data half already on this branch (`pipeline/night.py`, `pipeline/xml_parser.py`, `runbook/night.md`, the `night` family and its `index.json` sequences), the home seat strip and hex map components (`snapshots/hexmap.json`), `pipeline/build.py` route registration, `intent/nz-election/design-principles.md` and `look-538.md` (style, applied last), `product/nz_election/tests/screenshots.py`.

Branch: `change/nz-election-night-page` in `.worktrees/nz-election-night-page`, stacked on `change/nz-election-m3-night` (PR #59, under review). Do not edit `pipeline/night.py`, `pipeline/xml_parser.py` or their tests unless a page need forces it; if so, say which line and why in last.md.

Goal: rebuild the existing `/unattended/nz-election/night/` route from the night family, answering the plan's four questions in rank order. At 390x844, above the fold: the reporting line ("Results cover N percent of voting places, updated HH:MM", one thick progress bar, never "votes counted"), then the seat strip with the 62 line and the sentence "These combinations currently reach a majority; government formation is separate." Then the hex map coloured by current leader (shade by margin, uncounted grey) above a searchable electorate table (leader, margin, reporting status, link to each electorate page); then the status line "Preliminary; official results due 27 November". Before results: the countdown line and a link to vote/. Replay: `?sequence=<id>` plays a packaged sequence, starts paused, 1x/10x/60x, pause/reset, with a persistent label ("Illustrative replay based on 2023 final results", "Recorded demo", or "Final snapshot" for a lone archive) that no state can drop; no request to an official feed during a replay. Without JS the static snapshot tables render. Not shown: a replay presented as live, assumed special-vote totals, coalition agreements inferred from arithmetic. Absent means absent: no night data renders the countdown, vote/ link and the official results link only, never an empty chart or placeholder (m3_checks.py). Every figure: `aria-describedby`, `div.source-note`, `p.source-actions`. Live polling (increment 5) and the waterfall (increment 4) are out of scope.

Contracts: no route is added (79-route set unchanged); the screenshot registry gains named night states (2023 illustrative start, middle, end at 60x; recorded demo; each final archive; reset with focus; no-JS; absent night data), exact state coverage, not a lower bound. Tests on main at the base sha must not be weakened; this branch's own tests move with it.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass, including `test_replay_clock_pause_reset`, `test_final_snapshot_has_no_fake_timeline`, `test_illustrative_replay_label_persists`, `test_xml_python_browser_parity`, and a test that the replay makes no official-feed request.
- `uv run product/nz_election/pipeline/verify.py all` on a populated build prints `PASS all` (with `PASS night`).
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` prints PASS; name the night/ screenshots at 390 and 1280 per state.
- Question test (plan): from the 390x844 screenshot of the populated replay end state, say where answers 1 and 2 are and how far the reader scrolls to find an electorate.
- The replay end state shows 2,851,211 valid party votes and House 122.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
