# Campaign data: pollster record 2017, 2020, 2023 as a sourced snapshot (no page)

Data half of M3 increment 3 (`intent/nz-election/plan-m3.md`, "Increment 3" and its proof paragraph: the pollster scorecard rules), fetched once by you per issue #40. No route, no rendering, no daily family; the polls page (`intent/nz-election/pages/polls.md`, draft) will consume it later.

Read first: `AGENTS.md`, `intent/nz-election/plan-m3.md` (increment 3 paragraphs), `product/nz_election/snapshots/` with `snapshots.py` and its tests (same record shape: source URL, retrieved_at, licence note, per-record provenance; `donations.json` from PR #55 and `voting.json` are the nearest examples), `pipeline/poll_parser.py` only to reuse pollster and party naming.

Goal: `product/nz_election/snapshots/pollster-record.json`. For each pollster and each of the 2017, 2020 and 2023 general elections: its final eligible national party-vote poll before polling day (fieldwork end, publication before the election-day cutoff, explicit revision handling; exclude preferred-PM and electorate polls), the party shares it published, the official final party-vote shares (EC official results; denominator all valid party votes), signed error per party in percentage points (poll minus official), mean absolute error over comparable parties, and coverage (which parties were compared, which the poll did not report). Poll rows come from the Wikipedia "Opinion polling for the <year> New Zealand general election" pages at a pinned revision id (CC BY-SA 4.0, keep the revision link and attribution) or the pollster's own release; official shares from electionresults.govt.nz. Compare only parties the poll reported individually; never infer an absent party or fabricate a score. Keep arithmetic exact (decimal strings) until display; state the rounding rule.

A loader next to the existing snapshot loaders that validates the file and fails loudly with a named error: final poll's fieldwork end and publication are before that election's polling day, signed error equals poll minus official for every party, mean absolute error recomputes, every record has a source URL (Wikipedia with oldid, pollster, or EC domain) and retrieved_at, no pollster-year twice.

Constraints: no change to routes, page rendering, client code, workflows or the site harness; tests on main at the base sha are untouched except contracts that enumerate the snapshot set, which move with it. No secrets. Web access for Wikipedia, EC and pollster sites only.

Done when:
- `uv run --with pytest pytest -q product` passes, with new tests named after the plan where they fit (`test_scorecard_final_eligible_poll`, `test_scorecard_excludes_post_election_information`, `test_scorecard_party_errors_and_coverage`, `test_scorecard_absent_comparable_input`) plus a named-error test per loader check.
- `bin/lint` prints ok.
- last.md lists per year each pollster, its chosen poll (dates, revision link) and its mean absolute error, every pollster-year skipped and why, and `git diff --stat main` shows only snapshots, the loader and tests.
Commit in the worktree; do not push.
