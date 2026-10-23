# M3 increment 4: count, seat changes and electorate leaders on night/

Page plan: intent/nz-election/pages/night.md

Goal: build M3 increment 4 as written in `intent/nz-election/plan-m3.md` ("Increment 4" and
"Increment 4 proof"), answering night.md question 3 ("Who is ahead in my electorate?") in its
planned order: electorate table (leader, margin, reporting status, link to the electorate page)
and the hex map coloured by leader, uncounted grey, map above table. Questions 1 and 2 already
live on night/ from PR #60; keep their order and content.

Read first: `intent/nz-election/pages/night.md`, `intent/nz-election/plan-m3.md` (increment 4,
existing contracts, common verification), `product/nz_election/AGENTS.md`, the night parser and
package (`pipeline/xml_parser.py`, `pipeline/night.py`), `web/night*.mjs`, `REVIEW.md` pass 4.

New source facts (supervisor captures, commit dfdabe5 on this branch, manifest entries with
sha256): `product/nz_election/fixtures/ec-2026-media-xml/`. The 2026 preliminary feed is live at
`https://media.election.net.nz/xml/` (HTTPS 200, pre-election zero state). Path rule from the
public directory listing: `eNN/eNN.xml` per electorate (two digits, 1 to 71), voting places
`eNN/votingplaces/NN-NNNNN.xml`. A detail file has `<electorate e_no final updated>`,
`statistics` (total_voting_places, total_voting_places_counted, total_votes_cast, informals,
total_candidates), `partyvotes/party[p_no]/votes`, `candidatevotes/candidate[c_no]/votes`.
The national `election.xml` carries no electorate leaders, so leaders come only from detail
files. Two traps: the zero-state files say `final="true"` with 0 of 0 places counted, which must
never render as final or as a leader; and no `Access-Control-Allow-Origin` header is sent, so do
not design for browser fetches here (increment 5 decides transport; this increment reads detail
files present in the packaged snapshot and shows electorates without one as not yet reported).

Constraints: plan-m3 increment 4 rules bind (leaders provisional, never "elected"; places are not
votes; source-reported seats distinct from calculated; waterfall suppressed on incomplete inputs;
"Change since preliminary result" only with two compatible dated snapshots; no specials without
evidence). The 2023 replay must show leaders per electorate from data the repo already holds
(2023 per-electorate results), labelled illustrative as today. Contracts move with the registered
set: route count, family union, screenshot inventory and the capture pin (142) may change where
this increment adds states, never to a lower bound. Style from `design-principles.md` last. Do not
edit home or electorate page modules (another job may be on `build.py`/`screenshots.py`; keep
your edits there small and route-scoped). Commit in the worktree; do not push.

Done when all of these pass and you paste their last lines into last.md:
- `uv run --with pytest pytest -q` (all pass, including the seven named tests in the proof)
- `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py waterfall` prints `PASS waterfall`
- `... verify.py all` ends `PASS all`; `bin/lint` ok
- a test that parses each `ec-2026-media-xml` detail capture and asserts it yields no leader and
  no final status
- screenshots per the increment 4 proof at 390x844 and 1280x800, including selected electorate
  leader and the electorate table and map at replay end; say which files you looked at.
