# Build: `verify.py campaign` (schedule row Mon 2 Nov, requirement 12)

Goal: `uv run product/nz_election/pipeline/verify.py campaign` exists and prints exactly `PASS campaign` on
the deployed data, and fails with a named reason when the campaign data is wrong. Pipeline and checks only;
no template, CSS, route or page change (so no page plan applies). `verify.py all` includes it.

Read first: `intent/nz-election/spec.md` requirement 12 and the "Daily campaign" row of the data table;
`intent/nz-election/plan-m3.md` increment 3; `product/nz_election/pipeline/verify.py` (how `advance`,
`night`, `waterfall` are wired and how `--data` is honoured); `pipeline/donations.py`,
`pipeline/pollster_scorecard.py`, `pipeline/snapshots.py`, `pipeline/parties_page.py` (where the two
families are rendered today); `REVIEW.md`; `AGENTS.md`.

What the check asserts (name each invariant in code and in its FAIL message):
1. Donations: every row over the $20,000 threshold has party, donor, amount, a source document URL on an
   EC domain, and receipt/disclosure dates only where the source gives them (never the acquisition date
   standing in); the index row count is fully accounted for (rows plus listed omissions equal the index);
   no derived "total funding" figure exists in data or rendered output.
2. Pollster record: each scored poll is the final eligible national poll before the 2020 or 2023 election
   (no field dates after election day), party errors are against official shares, coverage is stated.
3. Advance voting: delegate to the existing `advance` check (do not duplicate it).
4. Rendered route(s) that show these families (find them; today the parties page) carry provenance for
   each figure and never render absent data as zero or a placeholder (reuse the existing ABSENT_TEXT gate).

Tests: `tests/test_campaign_verify.py` with one passing case on committed fixtures and one failing case per
invariant (malformed inputs built in the test, never as fake official captures). Tests on main at the base
sha must not be weakened; contracts that list the registered verify subcommands move with the new one.

Definition of done (run them, paste output in your final message):
- `uv run product/nz_election/pipeline/verify.py campaign --data <a checkout of origin/data's product/nz_election/data>` prints `PASS campaign`
  (if origin/data is not reachable in the sandbox say so; the supervisor runs it on the host)
- `uv run product/nz_election/pipeline/verify.py all` prints `PASS all`
- `uv run --with pytest pytest -q product/nz_election/tests/test_campaign_verify.py` passes, and the full
  suite `uv run --with pytest pytest -q product/nz_election` has no new failures
- `bin/lint` ok
Commit on the branch; do not push; do not commit `state/jobs/*/last.md`.
