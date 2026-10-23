Verdict: **request changes**.

Critical: None found.

Important:

- `product/nz_election/snapshots/pollster-record.json:7208`: Herald-DigiPoll is absent from both scores and exclusions. Pinned 2017 capture `801707892` contains its national poll dated 4-14 December 2015, with documented fieldwork and party shares. No stated age restriction excludes it; the scorecard includes YouGov’s 2019 poll for 2020. Add the eligible record or a justified, consistently applied exclusion.
- `product/nz_election/pipeline/pollster_scorecard.py:115`: Month-only dates are not validated against the documented month-end rule. Changing both candidate and scored Roy Morgan 2020 `fieldwork_end` from `2020-09-30` to `2020-09-29` still returns all 19 records. Validate the bound against the source month and add a rejection test.

Nit: None.

Checks completed:

- Five complete scored rows match capture bytes: 2017 Roy Morgan, Reid Research and Colmar Brunton; 2020 Colmar Brunton and Roy Morgan.
- All 19 records pass exact signed-error and MAE validation. Official vote counts match EC summaries for [2017](https://electionresults.govt.nz/electionresults_2017/statistics/overall-results-summary.html), [2020](https://electionresults.govt.nz/electionresults_2020/statistics/overall-results-summary.html) and [2023](https://electionresults.govt.nz/electionresults_2023/statistics/overall-results-summary.html).
- 120 malformed-field probes produced named errors. Existing tests on main are unchanged. No invented values found in checked rows or “not available” text in the snapshot.
- Exclusion completeness fails as above; no demonstrated bloc bias.

Verification limits: `uv run --with pytest pytest -q product` and `bin/lint` both failed before execution: `Failed to initialize cache ... Operation not permitted`. PR claims remain unchecked: `gh` could not connect; the connector requires reauthentication. No files changed.