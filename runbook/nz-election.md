# NZ election daily operations

The `NZ election daily` workflow runs on main at 15:43 UTC and can be dispatched by hand
from Actions, or with `gh workflow run nz-election-daily.yml --ref main`. Only Actions
publishes remote data. Do not push data locally.

Daily owns geography, candidates (including lists and review), baseline-2023, enrolment,
electorate-polls and markets. Hourly owns polls/averages/seats; social owns its own family.
All writers use the non-cancelling `nz-election-data-publication` group and a three-attempt
leased merge. Shared status, inventory and licences are regenerated from the merged union.
A family cannot replace a newer source acquisition with an older one.

The live daily run uses fetch.py for the Wikipedia candidates API and five allowlisted Gamma
events. Each request is capped at 2 MiB, with a 20-second timeout, at most three attempts,
bounded Retry-After and no redirects. Geometry, EC and other inputs remain immutable captures.
The default `daily_refresh.py --out <directory>` is offline verification and never fetches.
No raw market pages are published. Turnout is captured and validated but excluded from display.
Volume and liquidity display as rounded whole USD amounts under the supervisor's PR #30 fix-round instruction; normalized amounts remain exact decimal strings.

Read the daily Action summary and `data/status.json` row for each dataset. `last_attempt_at`
is the attempt time; `last_success_at` is ingestion time, not a new observation. The source
`fetched_at` and market `observed_at` retain acquisition times. `updated_at` is Gamma's own
update timestamp. The status message identifies successful acquisition or the failed attempt. Live failures never substitute fixture captures.
Candidate supplemental identity claims still require reviewed mappings; an incompatible live
revision fails that family rather than changing a reviewed claim's provenance.

A handled family failure retains its validated last-good bytes, marks stale (or unavailable on
first failure), uploads the validated status, and publishes before reporting failure. Unexpected
exceptions block upload. A failed live attempt keeps last-good bytes and success metadata unchanged; on first failure
the family is unavailable without any substituted capture. Only explicit offline runs ingest fixture captures. A daily ingestion is overdue after 36 hours, and the panel separately
reports old source observations. If publication keeps a newer remote family, its original
last-good run and acquisition remain authoritative.

After dispatch, inspect the publication summary, the union manifest and subsequent Pages run.
Pages responds to daily completion even on failure, resolves an exact data SHA separately from
code and retains the election freeze guard. Verify actual code/data HEADs in build-manifest.json,
markets.json/.csv and the home panel. Dispatch hourly next and check it retains daily files.

For rollback, dispatch `Publish the blog` on main with a reviewed compatible pair of `code_sha`
and `data_sha`, each 40 lowercase hex characters. M1 code cannot read M2 filenames. Always select
both compatible SHAs; never relax the unknown-file allowlist or rewrite the data branch to make
an older builder accept newer data. Inspect both actual checkout SHAs after the build.

Host visual acceptance: home `/` gained the markets module; `/downloads/` gains its catalogue
entries. Inspect both at 390x844 and 1280x800, including populated, unavailable and stale markets.
Run the existing all-route screenshot harness and coalition browser check. The panel shows the highest priced, non-placeholder Yes contract per event in three static tables.
The complete list remains a download only; no full-list route is published. Amounts sit in one
optional disclosure, with one rules link per event. The screenshot gate requires a maximum
844 px module height at width 390 and rejects unpriced/placeholder contracts on every page.
The existing M1/social recovery guide is `product/nz_election/runbook.md`.

## Harden gate

Run from the checkout root with the bundle and rendered site being accepted:

```sh
bin/nz-election-harden --data <bundle> --site <site> --history
uv run product/nz_election/tools/check_workflow_history.py --days 3
```

Every directory under `evals/` must contain `check.sh`; a missing script fails
with the eval name. The gate discovers and runs these scripts, then runs `verify.py all`, requiring
one explicit PASS for every registered family, including night, waterfall and
campaign, before the final `PASS all`. A polls-only bundle cannot satisfy Harden.
It then runs the social, social fix-round and night-operation freeze tests.
Checks continue after failures; the last line is `PASS harden` or
`FAIL harden: <first failing step>`, with exit status 0 or 1 respectively.
A SKIP or FAIL result line fails its step even when the process exits zero.
Read earlier output for all failures, including missing family lines.

History is enabled with `--history` and is required for milestone PASS. Without
it, an otherwise clean run prints `PARTIAL harden (history not checked)` and exits
1. Failures still print `FAIL harden`. A standalone history result does not change
a PARTIAL gate result; run the gate with `--history` for the milestone record.

The history command uses authenticated `gh run list` on main for every scheduled
workflow discovered in `.github/workflows/`. It covers the last three complete
Pacific/Auckland calendar days, excluding today. It reports run, success, failure
and recovery counts plus the reason for every failed workflow/day.

- Hourly workflow: gaps between consecutive successful runs are measured across
  midnight and must never exceed 3 hours. Each day's boundaries are the last
  success before it and the first success after it within the checked window.
  When no such success exists, use the window start or end respectively. Only
  the first day with no earlier data may use its own start; the last day uses
  its end. For example, 21:00 followed by 03:00 is a six-hour gap, not two
  three-hour gaps. Every failure must be followed by a success within 2 hours, including across midnight. The query includes a
  2-hour lookahead for recovery; runs beyond the checked window do not extend
  the gap boundaries. Runs outside a day never count toward that day's totals.
  Run counts are reported, not required,
  because GitHub can drop scheduled runs. Schedules with `*` in the cron hour field
  use this policy.
- Daily workflows: the last run of the day must have concluded success. A failure
  followed by a successful rerun that day is reported as a recovery. An earlier
  success cannot hide a later failed or pending run.

Day membership, run order and gaps use GitHub `createdAt` timestamps, measured in
elapsed time across NZ daylight-saving transitions. Cancelled, skipped and other
completed non-success runs count as failures; pending runs are not successes.
Scheduled and manually dispatched runs both count. A day without a cron run that
has a `workflow_dispatch` success is flagged for investigation; the same daily or
hourly policy still applies. Missing days, API errors and truncated history fail.

`--offline` skips the remote-data eval `pages-home-bytes-live` with a reason;
if combined with `--history`, history is also skipped. Every SKIP prevents an
overall PASS. Newly added evals run by default; register any new network eval in
`tools/harden.py` before using it offline. Save the date, code SHA, bundle/site
identity, full command output and last line in the daily acceptance record.
Offline fixture results demonstrate the checks, not live milestone acceptance.
