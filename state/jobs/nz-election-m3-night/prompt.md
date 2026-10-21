# M3 increment 2, data half: night parser, archives and the night family (no page)

Rescoped 2026-10-20 by the supervisor after the reader-first gate (issue #49, PR #50): the /night/ page waits for its own build from the page plan (`intent/nz-election/pages/night.md`, accepted). This job builds only what the page will read. Do not add or change any route, template, stylesheet, client script or screenshot registry entry.

Page plan: intent/nz-election/pages/night.md (this job builds only the data the plan names; the page is the next job)

Read first: `AGENTS.md`, `intent/nz-election/plan-m3.md` (shared contract, "Increment 2" and its proof), `intent/nz-election/spec.md` night requirements, `intent/nz-election/pages/night.md` (accepted 2026-10-20 14:33Z; it names the questions the data must answer, so keep fields it needs), `product/nz_election/fixtures/manifest.json` (entries for `ec-2017-xml/`, `ec-2020-xml/`, `ec-2023-xml/`, `ec-mediademo-xml/`), the existing golden 2023 checks and `allocator.py`.

Branch: `change/nz-election-m3-night` in `.worktrees/nz-election-m3-night`, rebased by the supervisor onto main (increment 1 merged as 605b316, main now 5cdcac8). Captures are committed by the supervisor: 2017 and 2020 quartets, the media demo reference files and two `election.xml` observations of the demo feed (simulated, not an election). Electorate detail paths were not observed in the demo feed; if you find them in the EC's own documentation or the feed, name the source URL in last.md and fetch at most one per observation; otherwise build without detail files and say so.

Goal (plan-m3 increment 2, data parts only): XML parser with reusable validation (Python, plus the JS parity module only if plan-m3 puts parsing in the client; no page uses it yet), `night/index.json` closed-world family with CSV siblings and atomic replacement, the deterministic "Illustrative replay based on 2023 final results" sequence as data, "Final snapshot" for a lone archive and "Recorded demo" for the demo observations as labelled states in the family, `runbook/night.md` (data side), `tests/night_smoke.py` against the family files. Replay controls, the page and its screenshots are the next job.

Contracts that move with this change: the registered family set gains `night`; the manifest entry count pin moves with the captures. Tests on `main` at 5cdcac8 must not be weakened; the branch's own tests move with it. No placeholder values for absent data (absent means absent).

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass, including the increment 2 data tests named in plan-m3 (list which named tests were left for the page job).
- `uv run product/nz_election/pipeline/verify.py night` prints exactly `PASS night`; `verify.py all` on a populated build prints `PASS all`.
- 2023 illustrative replay final state equals 2,851,211 valid party votes and House 122.
- `git diff --stat 5cdcac8` shows no file under templates, static or the screenshot registry.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
