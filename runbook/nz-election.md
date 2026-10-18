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
