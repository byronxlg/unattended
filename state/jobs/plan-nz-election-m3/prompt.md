# Plan job: M3 (election night, advance voting, campaign data)

Read-only planning job. Change no files. Your final message is the plan; the supervisor commits it as `intent/nz-election/plan-m3.md`.

## Goal

A build plan for spec requirements 9, 10, 11 and 12 (`intent/nz-election/spec.md`, "Election night", "Campaign data", "Election-night operation", and the M3 rows of the data table near line 131), due 1 November 2026, sized for at most five Codex build increments of about one day each. The engineer is gone after 5 November (last build dispatched then), so whatever election night (7 November NZDT, polls close 19:00) needs must be in these increments, and replay rehearsal must be possible from the first night increment.

## Read first

- `intent/nz-election/spec.md` (requirements 9 to 12, election-night operation, testing and acceptance, concerns about the XML WAF exemption and CORS near line 313 and decisions near line 358)
- `intent/nz-election/plan-m2.md` (shape and level of detail to match), `intent/nz-election/design-principles.md`, `intent/nz-election/home.md` (the results-first /night/ route already exists)
- `product/nz_election/AGENTS.md`, `product/nz_election/pipeline/` (verify.py checks, refresh, the existing XML parser and fixtures), the current `/night/` route source, `.github/workflows/` (hourly, daily, social daily, pages)
- `product/nz_election/fixtures/` capture manifests (what 2017/2020/2023 archive and exempt XML captures already exist)

## Constraints

- Static site on Pages fed by scheduled Actions; no server, no proxy. Browser polls the official feed no more than every 30 s, serially, national totals plus the selected electorate only, paused in hidden tabs, backoff on errors, last complete snapshot kept with a stale label.
- If the browser cannot fetch the feed (CORS or WAF), live mode shows the dated packaged snapshot and a link to the official results site. Say what probe proves browser access from the deployed origin and when it runs.
- Absent data is absent: no "not available" placeholder modules (design-principles.md); a module with no data is not rendered, enforced by a build check.
- Electoral Act s197 publication freeze on election day before 19:00 NZDT applies to polls, social and markets modules; say how the night build respects it.
- No new paid services; node_modules under 150 MB or no bundler; tests deterministic, network smoke tests separate.

## Definition of done (for the plan)

- Increments in order with: files touched (new and existing), fixtures needed and who captures them (mark any the supervisor must capture by hand, as plan-m2 did), proving tests by name, the `verify.py` line each must print (`PASS night`, `PASS waterfall`, `PASS advance`, `PASS campaign`), the screenshot states the harness must cover, and which existing test contracts move (route count, family union) with the registered set.
- Advance voting (req 11) ordered so it can publish from 26 October data; night replay (req 9) before count and seat changes (req 10).
- A rehearsal procedure: how the supervisor replays 2023 at 60x against the deployed site before 4 November, and what it checks.
- Disjointness: which increments can run in parallel with a design change touching the home and electorate templates.
- Open questions the supervisor must decide, each with your recommendation.
