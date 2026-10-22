# M3 increment 5: live night results through Actions, freeze on every publication path

Page plan: intent/nz-election/pages/night.md

Goal: build M3 increment 5 as written in `intent/nz-election/plan-m3.md` ("Increment 5",
"Increment 5 resilience, freeze and proof") with the "Increment 5 transport amendment"
(2026-10-22 20:20Z) overriding wherever they differ. Readers on night/ after 19:00 NZDT on
7 November see the preliminary count (night.md questions 1 to 3, already live from PRs #60 and
the increment 4 merge) update without reloading, from same-origin packaged JSON, with honest
stale and fallback states. Keep night/'s question order and content; this increment changes how
the data arrives, not what the page answers.

Read first: the amendment paragraph in `plan-m3.md`, `intent/nz-election/pages/night.md`,
`product/nz_election/AGENTS.md`, `pipeline/xml_parser.py`, `pipeline/night.py`, `web/night*.mjs`,
`deployment_guard.py`, `.github/workflows/pages.yml` and the hourly, daily and social workflows
(their freeze guards), `runbook/night.md`, `REVIEW.md` pass 4.

Source facts: the 2026 preliminary feed is `https://media.election.net.nz/xml/` (national files
plus `eNN/eNN.xml`, 1 to 71), HTTPS 200, no CORS header; captures in
`product/nz_election/fixtures/ec-2026-media-xml/` with manifest sha256. Pre-election zero-state
files say `final="true"` with 0 of 0 places counted: never final, never a leader. The demo feed
`https://mediademo.electionresults.govt.nz/xml/` changes over time; captures from increment 2 are
in the fixtures.

Shape (the amendment, in short): one workflow (name it, e.g. `nz-election-night-live.yml`,
`workflow_dispatch` only) that refuses to run before 19:00 NZDT 7 November (an injected-clock
test proves it), passes the same freeze guard as every other publication path, loops in one job
(reference set serially, then national plus 71 detail files, validated by the existing parser,
one complete cycle committed atomically to the data branch, Pages deploy only when the validated
cycle changed), cycle floor 5 minutes, timeout under 6 h with the next run chained before it ends,
concurrency group with cancel-in-progress false. A failed or partial cycle keeps the last good one.
A `--rehearsal` mode (or input) points it at mediademo or a recorded replay and publishes nowhere
but an artifact, so the supervisor can rehearse it through the real workflow before 7 November.
Browser: `web/night-live.mjs` polls the packaged JSON at most every 60 s, pauses on hidden tabs,
backs off, marks stale at 15 minutes against the cycle's retrieval time, and falls back to the
dated packaged snapshot with the official results link. Exports labelled "Packaged by the site".
You choose file and data shapes; the invariants are the plan's and the existing validators'.

Freeze: the publication block 6 November 23:30 NZDT to 7 November 19:00 NZDT covers polls,
social, markets, Pages deploys, manual dispatch, queued jobs and rollback; extend the existing
guard rather than writing a second one, and show `test_freeze_all_publication_paths` failing on
main for any path main leaves open.

Constraints: no secrets needed or added. Contracts move with the registered set: route count,
family union, screenshot inventory and capture pins may grow where this increment adds states,
never to a lower bound; tests on main at the base sha protect behaviour, not counts. Do not edit
home, vote, parties or electorate page modules. Style from `design-principles.md` last. Commit in
the worktree; do not push. Update `runbook/night.md` with the dispatch, rehearsal, stop and
rollback steps a human or the supervisor follows on the night.

Done when all of these pass and you paste their last lines into last.md:
- `uv run --with pytest pytest -q` (all pass, including the eight named tests in the proof)
- `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py night` prints `PASS night`
  and `... verify.py waterfall` prints `PASS waterfall`; `... verify.py all` ends `PASS all`
- `bin/lint` ok; `actionlint` on the new workflow if installed (say if not)
- a test that runs the workflow's fetcher against the zero-state captures and a recorded
  mediademo sequence with injected transport and clock, asserting serial order, the cycle floor,
  atomic commit and keep-last-good on a failed file
- screenshots per the increment 5 proof at 390x844 and 1280x800 (live fresh, stale last-good,
  packaged fallback, pre-close and post-close boundary); say which files you looked at.
