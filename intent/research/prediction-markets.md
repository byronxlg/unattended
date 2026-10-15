<!-- Copied verbatim by the supervisor on 2026-10-16 from state/jobs/research-prediction-markets-d1/last.md (Codex job research-prediction-markets-d1, read-only, web live). Curly quotes straightened and one arrow spelled out; nothing else changed. Supervisor review: intent/research/review-2026-10-16.md -->

# Landscape sweep: prediction-market tooling for an individual trader, 2026-10-16 (Codex research job research-prediction-markets-d1)

Method: read the lab'''s selection criteria and prior sweep, then searched live primary documentation, repositories, product pages and research.
GitHub observations are dated 2026-10-16 and **from page**, potentially cached; `gh api` failed with ''"error connecting to api.github.com''". Exact last-push timestamps were not found; explicitly labelled commit dates provide activity evidence.
Features are documented claims, not installation tests; footprints below are proposed budgets, and ''"not found''" means this sweep did not establish the fact.

## A. Official and community API clients and CLIs

All star counts in the tables were observed on **2026-10-16, from page**. Commit dates are not push timestamps.

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Polymarket unified Python SDK](https://github.com/Polymarket/py-sdk) | 139; push not found; [commit 2026-10-09](https://github.com/Polymarket/py-sdk/commits) | Official interface across public data, authenticated accounts, trading and wallet workflows. | MIT; local library without subscription. | Broad integration building block, not an individual'''s analytical journal. |
| [Polymarket py-clob-client-v2](https://github.com/Polymarket/py-clob-client-v2) | 167; push not found; [commit 2026-10-15](https://github.com/Polymarket/py-clob-client-v2/commits) | Books, prices, history, authenticated orders and fills; CLOB-focused. | MIT; public market reads do not need a signing key. | Gamma discovery and Data API portfolio reconciliation remain separate concerns. |
| [Polymarket CLI](https://github.com/Polymarket/polymarket-cli) | 2.9k; push not found; [commit 2026-05-26](https://github.com/Polymarket/polymarket-cli/commits) | Rust CLI with table/JSON output, discovery, books, prices, positions and trading commands. README calls it experimental. | Free; [manifest declares MIT](https://github.com/Polymarket/polymarket-cli/blob/main/Cargo.toml). | A generic CLI would duplicate existing work; persistence, risk attribution and forecasting discipline are different products. |
| [Kalshi official SDKs](https://docs.kalshi.com/sdks/overview) and [Python starter](https://github.com/Kalshi/kalshi-starter-code-python/) | SDK repository metadata not found; starter 101; push not found; [starter commit 2025-03-07](https://github.com/Kalshi/kalshi-starter-code-python/commits) | Sync/async Python and TypeScript SDKs. Docs warn SDKs may lag REST/OpenAPI and WebSocket/AsyncAPI; starter explicitly says it is not an SDK. | Public packages/examples; starter license not found. Public REST reads require no subscription setup. | Prefer current specifications over old examples; historical and live portfolio data need explicit reconciliation. |
| [PMXT](https://github.com/pmxt-dev/pmxt) | 2.2k; push not found; [commit 2026-07-18](https://github.com/pmxt-dev/pmxt/commits) | Unified Python/TypeScript API and CLI across Polymarket, Kalshi and other venues; capability coverage varies. | MIT; local server option requires Node. Hosted mode requires a PMXT key; current hosted price not found. | Normalisation already exists. A thin unified client is weak differentiation; hosted custody features are outside scope. |
| [Manifold API](https://docs.manifold.markets/api) and [manifoldpy](https://github.com/vluzko/manifoldpy) | API N/A; manifoldpy 41; push not found; [commit 2026-07-10](https://github.com/vluzko/manifoldpy/commits) | Official API exposes markets, bets, probabilities, user metrics and resolution fields. Community Python wrapper also computes accuracy metrics; README says its API wrapper is no longer maintained. | Public reads without authentication; wrapper MIT. API still labelled alpha. | Useful forecasting context; its market mechanics and mana-denominated results should not be treated as interchangeable with cash-market order books. |

**Polymarket access.** Gamma supplies discovery/metadata; CLOB supplies books and prices; Data API v2 supplies public wallet positions, activity, P&L and resolution state without authentication. No read-access charge is documented on these pages. Private CLOB account operations require credentials; a public-wallet observer need not receive a private key. The legacy `py-clob-client` is listed as archived. [API overview](https://docs.polymarket.com/api-reference/predictions/overview), [Data API v2](https://docs.polymarket.com/api-reference/data-api/overview), [repository listing](https://github.com/orgs/Polymarket/repositories).

**Polymarket limits and geography.** Published IP limits include Gamma `/markets` 300 requests/10 seconds, `/events` 500/10 seconds; CLOB `/book` 1,500/10 seconds and `/prices-history` 1,000/10 seconds; Data v2 overall 800/10 seconds, positions and price history each 200/10 seconds. The geographic page currently lists **New Zealand as close-only on both frontend and API**. That contradicts any assumption that new trading from New Zealand remains unrestricted; the page describes order restrictions, not a blanket prohibition on public reads. The [terms URL](https://polymarket.com/tos) did not expose substantive terms through this fetch, so storage/redistribution permissions remain unverified. [Rate limits](https://docs.polymarket.com/api-reference/rate-limits), [geographic restrictions](https://docs.polymarket.com/api-reference/geoblock).

**Kalshi access and terms.** Public REST markets and books are unauthenticated; WebSocket access and private portfolio endpoints require authentication. Current SDK docs support RSA signing, with Ed25519 requiring SDK 3.31.0+. Basic authenticated read budget is 200 tokens/second, usually 10 tokens/request, equivalent to 20 ordinary reads/second; the unauthenticated budget was not found. No public-read charge is stated in the quickstart. The Developer Agreement restricts API use and caching to facilitating a member'''s own Kalshi trading, prohibits sharing API data without written authorisation, and includes public-statement restrictions. Website Data Terms separately restrict software development and redistribution. Consequently, technical accessibility does not establish permission for a public cross-venue data product. International eligibility requires residence verification and the Member Agreement; New Zealand eligibility was not established. [Public reads](https://docs.kalshi.com/getting_started/quick_start_market_data), [limits](https://docs.kalshi.com/getting_started/rate_limits), [Developer Agreement](https://kalshi-public-docs.s3.amazonaws.com/Kalshi-Developer-Agreement.pdf), [Data Terms](https://kalshi-public-docs.s3.amazonaws.com/kalshi-data-terms-of-service.pdf), [international eligibility](https://help.kalshi.com/en/articles/14026044-can-i-trade-on-kalshi-from-outside-the-united-states).

**Manifold access and terms.** Public market/bet/user reads have no documented read fee; authenticated operations use an API key or JWT. Limit: 500 requests/minute/IP, with circumvention prohibited. API-based personal projects are permitted; non-API scraping and commercial AI-training use without a licence are prohibited. No New Zealand-specific public-read restriction was found; terms require compliance with applicable local law. [API](https://docs.manifold.markets/api), [terms](https://docs.manifold.markets/terms).

## B. Portfolio tracking and P&L

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [byronxlg/polymarket-tui](https://github.com/byronxlg/polymarket-tui) | 5; push/commit date not found | Books, trades, charts, portfolio/P&L, watchlist and trader following. | MIT; local Python terminal application. | Direct existing substitute belonging to Byron'''s public namespace. A new portfolio viewer needs a stronger reason than terminal convenience. |
| [LuciferForge/polymarket-pnl](https://github.com/LuciferForge/polymarket-pnl) | 8; push not found; [commit 2026-06-21](https://github.com/LuciferForge/polymarket-pnl/commits) | Wallet-address CLI; API-reported cash/realised P&L, categories, positions, CSV/JSON export. | MIT; Python stdlib, no API keys. | Already occupies ''"one command tells me my P&L''". README does not establish independent fee/lifecycle accounting. |
| [LuciferForge/pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) | 0; push not found; [commit 2026-05-16](https://github.com/LuciferForge/pnl-truthteller/commits) | Claims fill/slippage reconciliation against bot records; SQLite and JSONL input; Markdown reports. | MIT; read-only Python package. | Reconciliation itself is occupied. Its advertised wallet-only CLOB fill access needs validation; the sweep did not verify it. |
| [Polymarket Analytics](https://polymarketanalytics.com/) | N/A; deployment activity not found | Advertises realised/unrealised P&L, entries, trade history, wallet lookup, resolved-market history and candle exports. | Hosted; source not found. Free browsing; [pricing page](https://polymarketanalytics.com/pricing) lists Premium at $20/month on 2026-10-16. | Local reproducibility and transparent accounting assumptions could differ; ordinary dashboards and exports do not. Fee-accounting completeness was not established. |
| [Dune: Polymarket Combo Top Traders](https://dune.com/theliam/polymarket-combo-top-traders) | N/A; page reports validation on 2026-09-14 | Settlement-valued combo trading P&L net of exchange fees, maker/taker attribution and valued-volume coverage. Explicitly excludes gas, rebates, transfers and several lifecycle operations. | Public dashboard and inspectable SQL; hosted engine. Current query/API pricing not found in the fetched [pricing page](https://dune.com/pricing). | Strong methodological baseline, but neither total wallet P&L nor an offline personal ledger. |
| [PolymarketWhales Observations](https://polymarketwhales.online/) | N/A; deployment activity not found | Read-only large-trade feed, clusters, accumulation and bursts; page states 15-minute updates. | Public hosted page; source and paid pricing not found. | Surveillance of other wallets, not fee-aware accounting or risk on one'''s own positions. Similar names denote different products. |

The official API already offers an [accounting snapshot](https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs) containing `positions.csv` and `equity.csv`. Data v2 distinguishes open, redeemable, lost-redeemable, mergeable and closed positions. These are reasons to test official output before proposing another exporter. [Data v2](https://docs.polymarket.com/api-reference/data-api/overview).

A possible accounting distinction is an **explainable residual**: opening equity plus external cash flows plus attributed gains should reconcile to closing equity, with unknown fees, transfers or missing history shown explicitly. Whether public endpoints support that sufficiently is an unresolved feasibility question, not an established gap that twelve days will solve.

## C. Calibration and forecasting skill

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Fatebook](https://github.com/Sage-Future/fatebook) | 64; push not found; [commit 2026-06-12](https://github.com/Sage-Future/fatebook/commits) | Personal predictions, integrations and [export of predictions](https://fatebook.io/); [published statistics](https://fatebook.io/global-stats) include Brier scores. | MIT web application; hosted subscription price not found. Self-hosting involves a larger application than a CLI. | Strong substitute for recording beliefs; no traded-position linkage or market-close benchmark was established. |
| [manifoldpy](https://github.com/vluzko/manifoldpy) | 41; push not found; commit 2026-07-10, as above | Brier/log scores, calibration and market probability histories. | MIT; library rather than complete personal workflow; maintenance caveat above. | Demonstrates that scoring formulas are not novel. Porting across resolution semantics and joining personal forecasts to trades remain work. |
| [properscoring](https://github.com/properscoring/properscoring) | 188; push not found; [commit 2022-10-12](https://github.com/properscoring/properscoring/commits) | Python proper-scoring functions, including Brier-related calculations and continuous-distribution scores. | Apache-2.0; NumPy/SciPy, optional Numba. | Mature mathematical building block; no identity, forecast timestamps, venue ingestion or trading journal. |
| [Metaculus exports/API](https://www.metaculus.com/api/) | Hosted service; relevant repository metadata not assessed; deployment activity not found | Download ZIPs of CSVs and retrieve one'''s forecasts/scores. Official scoring is time-weighted and log-score-based, not simply binary Brier. | Token required for all API requests. Own data available to authenticated users; broader aggregate access restricted. Commercial use and AI/ML development require written permission. Numeric rate limit not found. | Good import source for an individual; cannot assume unrestricted community-history access or score comparability. [Scoring FAQ](https://www.metaculus.com/help/scores-faq/). |

A fill price records a transaction, not the trader'''s subjective probability. A calibration tool should request a timestamped belief explicitly; score market prices separately. Compare against the market **at forecast time** for a fair information benchmark, and against a precisely defined pre-close quote as a separate diagnostic. Repeated fills on one event should not masquerade as independent forecasting successes.

## D. Market scanners and alerting

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [al1enjesus/polymarket-whales](https://github.com/al1enjesus/polymarket-whales) | 64; push not found; [commit 2026-03-20](https://github.com/al1enjesus/polymarket-whales/commits) | Terminal whale alerts, Telegram/Discord notifications and CSV/JSON export. | MIT; local Python process. Direct public-data operation avoids a paid data service; continuous monitoring requires an awake machine. | Large-trade alerts are occupied. README also promotes a third-party relay; that is unnecessary for the proposed read-only products. |
| [Kalshi Alerts Telegram Bot](https://github.com/harish-garg/Kalshi-Alerts-Telegram-Bot) | 1; push not found; [commit 2025-12-15](https://github.com/harish-garg/Kalshi-Alerts-Telegram-Bot/commits) | WebSocket subscriptions, reconnects, SQLite subscriptions and price-change alerts; default threshold five cents. | README declares MIT; Python, Kalshi credentials and Telegram bot token. No software subscription stated; hosting/power remains the operator'''s cost. | Volume alerts, open/close notifications and daily summaries are listed as future enhancements. Not a portfolio-liquidity monitor. |
| [nl2992/prediction-pipeline](https://github.com/nl2992/prediction-pipeline) | 1; push not found; [commit 2026-10-03](https://github.com/nl2992/prediction-pipeline/commits) | Polymarket/Kalshi catalog matching, live books, depth-walked divergence, fees, alerts and settlement checks. | Public Python source; licence not found. Read-only demo claims no credentials; SMTP service may add cost. Kalshi contractual limits still apply. | A serious near-neighbour: even fee/depth-aware matching is occupied. README documents false matches and corrections rather than proving reliable arbitrage. |

Coverage is uneven: whale and price alerts have direct implementations; the Kalshi bot leaves lifecycle notifications unfinished. This sample did not establish a lightweight tool combining **new-market filters, own-position exit depth, spread deterioration, approaching deadlines, changed resolution wording and resumable local alert history**. That absence is narrower than ''"no scanners exist''".

## E. Research and analysis

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
| --- | --- | --- | --- | --- |
| [Polymarket historical APIs](https://docs.polymarket.com/api-reference/data-api/overview) | N/A; deployment activity not found | Data v2 documents minimum retention of 7 days at one-minute serving, 60 days at five-minute, 90 days at thirty-minute; twelve-hour history permanent, three-hour from July 2026. [CLOB batch history](https://docs.polymarket.com/api-reference/markets/get-batch-prices-history) accepts up to 20 assets. | Public reads; no read charge documented; endpoint limits in A. | Older fine-grained observations cannot be assumed available. Requested bucket width does not guarantee dense observations. Price history is not historical full-depth books. |
| [Kalshi historical API](https://docs.kalshi.com/getting_started/historical_data) | N/A; deployment activity not found | Separate archived markets, trades, fills, orders and positions, selected using cutoff timestamps. [Historical candles](https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks) support 1/60/1,440-minute intervals. [Batch candles](https://docs.kalshi.com/api-reference/market/batch-get-market-candlesticks) allow 100 tickers and 10,000 candles total. | Public market history versus authenticated personal history; no endpoint price documented. Developer Agreement constrains reuse. | Must join live and archived data without gaps or duplicates. Historical full-depth book endpoint not found. |
| [Manifold data downloads](https://docs.manifold.markets/data) | N/A; page says dumps last updated 2024-07-06 | Historical markets, bets and comments; listed bets dump 967 MB, markets 87 MB, comments 127 MB. | Free personal/non-commercial dumps; commercial licensing quoted separately. | Stale bulk download is a poor fit for the host'''s disk constraint. Targeted API requests fit better. |
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | 3.9k; push not found; [commit 2026-10-09](https://github.com/Jon-Becker/prediction-market-analysis/commits) | Python/uv collectors, API/blockchain trade history, Parquet storage and analysis framework producing figures/statistics. | MIT code; default dataset download is **36 GiB compressed**. Data-use rights remain separate from code licensing. | Useful methodology and code reference; default research workflow cannot fit this lab. Small event-window analysis would need selective collection. |

## Research or practitioner baselines

- **Scoring baseline:** Metaculus defines binary Brier as `(p - outcome)^2`: perfect predictions score 0; always forecasting 50% scores 0.25. It separately documents time-weighted scores. Use declared scoring conventions, event counts and horizons before comparing systems. [Brier methodology](https://www.metaculus.com/notebooks/16708/exploring-metaculuss-ai-track-record/), [time weighting](https://www.metaculus.com/help/scores-faq/).
- **Forecasting versus liquidity provision:** Becker'''s write-up reports 72.1 million Kalshi trades and mean excess returns of -1.12% for takers versus +1.12% for makers. This is the author'''s historical analysis, not a net-return promise for Byron; it motivates separating forecasting skill from execution role. [Write-up](https://www.jbecker.dev/research/prediction-market-microstructure).
- **Arbitrage exists, but accessibility is unproven:** *Unravelling the Probabilistic Forest* estimates $40 million in extracted arbitrage profit. Its historical market-wide estimate does not establish that a small trader polling from New Zealand can capture current opportunities. [Paper](https://arxiv.org/abs/2508.03474).
- **Microstructure measurement can fail:** a Polymarket study reports approximately 59% agreement between trade direction inferred from public book-feed buckets and on-chain ground truth. It uses 30 billion events over 52 days. This bounds both the credibility of casual order-flow claims and the infeasibility of reproducing a full archive locally. [Paper, revised 2026-05-14](https://arxiv.org/abs/2604.24366).
- **Matching is a substantial product problem:** prediction-pipeline'''s README reports that 13 of its top 16 apparent opportunities were mismatches before one correction pass; a documented full catalog scan took 619 seconds. These are author-reported examples, not independently replicated benchmarks. [Practitioner record](https://github.com/nl2992/prediction-pipeline).
- **Accounting definitions matter:** the Dune combo dashboard reports checking 1,009,300 redemptions with no differences above 0.000002 pUSD, while explicitly excluding several components of whole-wallet returns. Narrow reconciliation with stated exclusions is a more credible target than claiming ''"true P&L''". [Dashboard methodology](https://dune.com/theliam/polymarket-combo-top-traders).

## Unoccupied niches

These are **not found in the checked sample**, not claims of global absence.

1. **A local belief-to-trade scorecard:** timestamp personal probabilities, join positions, and compare with contemporaneous and pre-close market forecasts.
   Evidence: Fatebook and scoring libraries cover beliefs/scores; portfolio tools cover transactions. A maintained, small integration covering both was not established.
2. **A personal portfolio exception monitor:** report disappearing exit liquidity, concentration, stale marks, approaching resolution and changed settlement text.
   Evidence: checked alert tools prioritise whales, price thresholds or cross-venue opportunities; Byron'''s TUI already handles ordinary viewing.
3. **A bounded accounting reconciliation report:** distinguish trading gains, valuation changes, cash movements and unresolved differences, with source coverage attached.
   Evidence: official exports and P&L tools already exist; truthteller focuses on fills, while Dune explicitly limits its accounting scope. Complete lightweight wallet reconciliation was not demonstrated.

## Candidate products

Each proposal is an alternative twelve-day build, not a combined roadmap. All use Python with `uv`, standard-library SQLite/HTTP/Decimal where practical, synthetic test fixtures, and local reports. No Docker, bulk datasets, paid APIs, signing keys, order submission or money movement. Commands below are proposed acceptance interfaces, not commands executed during this research.

### 1. Forecast Ledger

**Pitch:** a local journal that tests whether Byron'''s stated probabilities add information beyond the market, while keeping trading returns separate.

1. Days 1-2: ship timestamped forecast entry, revisions and CSV export; verify `uv run forecast demo --check` against known records.
2. Days 3-4: ship Polymarket metadata and contemporaneous quote capture with freshness fields; verify `uv run forecast sync --fixture sparse-market --check`.
3. Days 5-6: ship binary resolution import and Brier scoring, explicitly excluding unresolved/void cases; verify `uv run forecast score --fixture scoring-cases --check`.
4. Days 7-9: ship same-time and pre-close comparisons, event grouping and missing-baseline counts; verify `uv run forecast benchmark --fixture hindsight-traps --check`.
5. Days 10-12: ship weekly Markdown/HTML review and user-owned forecast CSV imports; verify `uv run forecast acceptance --offline`, including duplicate/revision handling.

**Footprint:** target under 250 MiB including a managed Python environment, under 100 MiB RAM, 25 MiB retained journal/cache; on-demand runs and optional daily refresh. Estimates, not measurements.
**User and weekly use:** Byron and small discretionary traders review where beliefs were informative, overconfident or unsupported; optional Fatebook/Metaculus import starts with files.
**Daily-blog interest:** visible demonstrations of hindsight leakage, why winning trades can reflect poor forecasts, and how a small sample changes the report'''s claims.
**Strongest argument against:** requires recording beliefs before outcomes; existing Fatebook plus a spreadsheet may suffice. Twenty lab days may produce too few independent resolutions to demonstrate improved skill.

### 2. Position Watch

**Pitch:** an address-only Polymarket monitor that tells Byron when something material changes in positions he already owns.

1. Days 1-2: ship complete paginated position snapshots with explicit missing/stale data; verify `uv run watch snapshot --fixture pagination --check`.
2. Days 3-4: ship book-based exit-value estimates for actual held size, alongside midpoint marks; verify `uv run watch liquidity --fixture thin-book --check`.
3. Days 5-6: ship manually labelled event groups, concentration and scenario-loss summaries; verify `uv run watch risk --fixture correlated-events --check`.
4. Days 7-9: ship deadline/resolution-state alerts, stored settlement-text diffs and deduplication; verify `uv run watch replay --fixture lifecycle --check`.
5. Days 10-12: ship resumable scheduling, retention limits and local daily/weekly digests; verify `uv run watch acceptance --offline` with restart and outage cases.

**Footprint:** target under 250 MiB installed, under 100 MiB RAM, capped 100 MiB SQLite history; approximately 20 watched markets with minute-scale polling, not a whole-market stream. Free on an existing awake Mac.
**User and weekly use:** Byron checks concentrated exposures, positions difficult to exit, unresolved outcomes and changes missed while away.
**Daily-blog interest:** demonstrate why a displayed mark differs from an executable exit, show an alert surviving a restart, and replay a resolution change.
**Strongest argument against:** may be better as a small extension to Byron'''s existing TUI. A sleeping laptop cannot provide continuous alerts, and incomplete resolution metadata limits what can be detected.

### 3. Portfolio Reconciliation Notebook

**Pitch:** explain weekly changes in one Polymarket wallet and show the unexplained remainder instead of presenting an unsupported precise total.

1. Days 1-2: ship imports of official accounting snapshots and activity, preserving source timestamps; verify `uv run reconcile ingest --fixture overlapping-pages --check`.
2. Days 3-4: ship Decimal-based cash-flow and position accounting for ordinary binary buys/sells; verify `uv run reconcile ledger --fixture partial-sales --check`.
3. Days 5-6: ship explicit resolution, redemption, fee and reward treatment; unsupported transfers/splits/merges become exceptions; verify `uv run reconcile ledger --fixture lifecycle --check`.
4. Days 7-9: ship equity bridges and discrepancy attribution against official snapshots; verify `uv run reconcile bridge --fixture missing-fee --check`.
5. Days 10-12: ship weekly CSV/Markdown reports with coverage and manual corrections recorded separately; verify `uv run reconcile acceptance --offline`.

**Footprint:** target under 250 MiB installed, under 100 MiB RAM, capped 100 MiB wallet history; incremental on-demand fetching, no chain-wide indexer or paid RPC.
**User and weekly use:** Byron reconciles deposits/withdrawals, resolved gains and marked positions, then investigates only material discrepancies.
**Daily-blog interest:** construct small cases where two plausible P&L calculations disagree and show the accounting explanation.
**Strongest argument against:** public feeds may not expose enough information for trustworthy whole-wallet accounting. Official exports plus existing reconciliation tools may already cover Byron'''s needs; handling every token lifecycle exceeds twelve days.

## Sources

All links below were consulted for claims used in this document; repository commit pages support activity dates, not exact push timestamps.

- Polymarket unified SDK: [repository](https://github.com/Polymarket/py-sdk), [commits](https://github.com/Polymarket/py-sdk/commits).
- Polymarket CLOB V2: [repository](https://github.com/Polymarket/py-clob-client-v2), [commits](https://github.com/Polymarket/py-clob-client-v2/commits).
- Polymarket CLI: [repository](https://github.com/Polymarket/polymarket-cli), [commits](https://github.com/Polymarket/polymarket-cli/commits), [licence declaration](https://github.com/Polymarket/polymarket-cli/blob/main/Cargo.toml).
- Polymarket: [repository status listing](https://github.com/orgs/Polymarket/repositories), [API overview](https://docs.polymarket.com/api-reference/predictions/overview).
- Polymarket: [Data API v2](https://docs.polymarket.com/api-reference/data-api/overview), [rate limits](https://docs.polymarket.com/api-reference/rate-limits), [geography](https://docs.polymarket.com/api-reference/geoblock), [terms fetch](https://polymarket.com/tos).
- Polymarket: [accounting export](https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs), [batch price history](https://docs.polymarket.com/api-reference/markets/get-batch-prices-history).
- Kalshi: [SDK guidance](https://docs.kalshi.com/sdks/overview), [starter](https://github.com/Kalshi/kalshi-starter-code-python/), [starter commits](https://github.com/Kalshi/kalshi-starter-code-python/commits).
- Kalshi: [public REST reads](https://docs.kalshi.com/getting_started/quick_start_market_data), [rate limits](https://docs.kalshi.com/getting_started/rate_limits).
- Kalshi: [Developer Agreement](https://kalshi-public-docs.s3.amazonaws.com/Kalshi-Developer-Agreement.pdf), [Data Terms](https://kalshi-public-docs.s3.amazonaws.com/kalshi-data-terms-of-service.pdf), [international eligibility](https://help.kalshi.com/en/articles/14026044-can-i-trade-on-kalshi-from-outside-the-united-states).
- Kalshi: [historical-data routing](https://docs.kalshi.com/getting_started/historical_data), [historical candles](https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks), [batch candles](https://docs.kalshi.com/api-reference/market/batch-get-market-candlesticks).
- PMXT: [repository](https://github.com/pmxt-dev/pmxt), [commits](https://github.com/pmxt-dev/pmxt/commits).
- Manifold: [API](https://docs.manifold.markets/api), [terms](https://docs.manifold.markets/terms), [data downloads](https://docs.manifold.markets/data).
- manifoldpy: [repository](https://github.com/vluzko/manifoldpy), [commits](https://github.com/vluzko/manifoldpy/commits).
- Byron'''s [Polymarket TUI](https://github.com/byronxlg/polymarket-tui).
- polymarket-pnl: [repository](https://github.com/LuciferForge/polymarket-pnl), [commits](https://github.com/LuciferForge/polymarket-pnl/commits).
- pnl-truthteller: [repository](https://github.com/LuciferForge/pnl-truthteller), [commits](https://github.com/LuciferForge/pnl-truthteller/commits).
- Polymarket Analytics: [features](https://polymarketanalytics.com/), [pricing](https://polymarketanalytics.com/pricing).
- Dune: [combo P&L dashboard/methodology](https://dune.com/theliam/polymarket-combo-top-traders), [pricing fetch](https://dune.com/pricing).
- [PolymarketWhales Observations](https://polymarketwhales.online/).
- Fatebook: [repository](https://github.com/Sage-Future/fatebook), [commits](https://github.com/Sage-Future/fatebook/commits), [application/export](https://fatebook.io/), [scoring statistics](https://fatebook.io/global-stats).
- properscoring: [repository](https://github.com/properscoring/properscoring), [commits](https://github.com/properscoring/properscoring/commits).
- Metaculus: [API/export permissions](https://www.metaculus.com/api/), [scoring FAQ](https://www.metaculus.com/help/scores-faq/), [Brier methodology](https://www.metaculus.com/notebooks/16708/exploring-metaculuss-ai-track-record/).
- polymarket-whales: [repository](https://github.com/al1enjesus/polymarket-whales), [commits](https://github.com/al1enjesus/polymarket-whales/commits).
- Kalshi alert bot: [repository](https://github.com/harish-garg/Kalshi-Alerts-Telegram-Bot), [commits](https://github.com/harish-garg/Kalshi-Alerts-Telegram-Bot/commits).
- prediction-pipeline: [repository and practitioner record](https://github.com/nl2992/prediction-pipeline), [commits](https://github.com/nl2992/prediction-pipeline/commits).
- Prediction Market Analysis: [repository](https://github.com/Jon-Becker/prediction-market-analysis), [commits](https://github.com/Jon-Becker/prediction-market-analysis/commits), [Becker'''s microstructure write-up](https://www.jbecker.dev/research/prediction-market-microstructure).
- Research: [Unravelling the Probabilistic Forest](https://arxiv.org/abs/2508.03474), [Polymarket order-book microstructure](https://arxiv.org/abs/2604.24366).