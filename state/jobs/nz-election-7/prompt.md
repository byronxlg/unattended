# Build brief: nz-election increment 7 (markets and daily automation)

You are the engineer in the unattended lab (read AGENTS.md, then product/nz_election/AGENTS.md).
You are in the worktree `.worktrees/nz-election-7` on branch `change/nz-election-7`, based on
main at 29bf079 (increment 6, the design system PR #21, the social proof of concept PR #24,
the social and polls fixes #25 #27 #28 and the feed home H-a PR #29 are merged and live: the
root is now the election hub of rule-separated modules per intent/nz-election/home.md, and the
polls page moved to /polls/). The branch carries one supervisor commit, 37e3b9d: the five
Polymarket Gamma event captures and their manifest entries. Commit there; never push. No
network in your sandbox; builds and tests are offline.

## Goal

Increment 7 of intent/nz-election/plan-m2.md "Build order": normalized markets, the static
markets panel, the daily workflow, the Pages trigger and the operational runbook (spec
requirement 5 as amended by decision 5: markets are a dated daily panel). Read, in order:
plan-m2.md "Before increment 7" (the five captures and what test_required_gamma_captures
gates), "Data contracts and family boundaries" (the markets.json row and the markets family),
"Markets", "Daily refresh, publication and Pages", "Design and accessibility", "Verification
and test inventory" (test_markets.py by name; the daily and race tests), "Build order" and
"Supervisor decisions" (decisions 5, 6, 8, 9 and 10 bind this increment); spec.md requirement 5
and its licence row; then the code: pipeline/daily_refresh.py, daily_sources.py, publish.py
(success_order, the family ownership and the lease), export.py (families, validators),
build.py, presentation.py, verify.py, fetch.py (the bounded transport the hourly uses),
deployment_guard.py, web/templates/base.html, home.html and polls.html, intent/nz-election/home.md, web/styles.css,
tests/test_contracts.py, test_pipeline.py, test_workflows.py, screenshots.py, design_checks.py,
config/{routes,sources}.json, fixtures/manifest.json, .github/workflows/{nz-election-hourly,
nz-election-social-daily,pages}.yml, runbook/nz-election.md.

## Inputs already on the branch (do not refetch, do not edit)

- `fixtures/polymarket/<slug>.json` for the five slugs in plan-m2.md "Before increment 7":
  each a Gamma events array with one event; markets per event 34, 6, 7, 7, 6; outcomePrices
  and outcomes are JSON-encoded strings inside each market; `updatedAt` is the upstream
  timestamp, `captured_at` in the manifest is the observation time. Turnout is captured and
  excluded from display with the manifest's recorded reason (decision 9).
- `fixtures/manifest.json`: 116 entries (was 111; `test_capture_manifest` counts them, update it).
- Unit evidence: the capture has no unit field for volume or liquidity and the supervisor has
  not committed Gamma documentation evidence. Per "Markets": label the unit unavailable, show
  the bare amount with that label, never print a currency symbol. The refinement round may
  add the evidence.

## Contracts that move with this increment (build, not fix: say which in last.md)

- `test_capture_manifest` 111 to 116. Route count stays 79 (H-a made it 79) unless the panel is a new route
  (it is not: it is one more module region on the home hub, under `#polls` per home.md line 49 (plan-home.md "Markets" reserved the slot), in the home.md
  module style, no rating labels; plan-m2.md "Markets" says home). The family union in test_contracts.py
  and the publication ownership tests gain `markets` under daily ownership (decision 6).
- Everything else in tests/ stays as it is; new tests go in new files or appended.

## Constraints

- The invariants and where they are enforced: prices are decimal strings in [0, 1] validated
  in export.py's family validator; display is price times 100 with display-only rounding in
  presentation.py; markets never enter allocation (seats.py, coalitions.py untouched);
  `success_order` treats a missing `fetched_at` as empty (publish.py:32, a known gap, cover it
  with a test). Choose the shapes yourself within the plan's row contract.
- Daily workflow `nz-election-daily.yml`: cron 43 15 * * *, workflow_dispatch, main only,
  `nz-election-data-publication` concurrency, cancel-in-progress false, `--family daily`,
  validated-only upload, publish in a separate job with contents write, fetches the Wikipedia
  candidates page and the five Gamma events live through fetch.py's bounded transport
  (second allowed host gamma-api.polymarket.com, response cap, retries), and falls back to
  the committed captures with the status row saying so. Add it to pages.yml's workflow_run
  list without touching the s197 guard or the social workflow. Mirror the hourly's steps and
  test_workflows.py's checks; do not weaken any of them.
- Design: the panel reuses the shared shapes design_checks.py enforces (figure with
  aria-describedby, p.source-actions for links, the provenance chip, counts inside figures,
  no meaning by colour alone); the exact attribution line from spec.md's licence row; "Market
  price", never "Poll"; three separate tables (next PM, government membership, seat bands);
  unavailable and stale states rendered honestly with the observation time. Run the design
  checks on the populated state, not only the empty state.
- Runbook: a daily section in runbook/nz-election.md (dispatch by hand, read the status row,
  the rollback pair rule from the plan's Concerns). No raw market pages copied.

## Definition of done (output in last.md, kept untracked)

- `uv run --with pytest pytest -q product/nz_election`: all passed, count stated, the new tests
  listed by name (target about 22; explain the actual count).
- `uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/m7-data && uv run
  product/nz_election/pipeline/daily_refresh.py --out /tmp/m7-data && uv run
  product/nz_election/pipeline/build.py --data /tmp/m7-data --out /tmp/m7-site/nz-election &&
  uv run product/nz_election/pipeline/verify.py --data /tmp/m7-data --site /tmp/m7-site all`:
  `PASS refresh: daily bundles`, `PASS build: 79 routes`, `PASS markets`, ending `PASS all`
  (move any previous /tmp/m7-data aside first).
- `bin/lint` ending lint ok.
- Screenshots and the coalition browser run on the host by the supervisor (no browser in the
  sandbox); say which routes changed so the supervisor looks at them at 390 and 1280.
- One or two commits on the branch, not pushed, no amend of 37e3b9d.
