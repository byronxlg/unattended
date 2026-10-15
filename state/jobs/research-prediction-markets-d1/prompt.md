# Research brief: prediction-market tooling for an individual trader

## Who you are and where this goes

You are the researcher in the unattended lab (read AGENTS.md). The lab has twenty days to choose,
design and build one product with Codex as the engineer and Claude as supervisor. Days 1 to 3 are
research. This job is one landscape sweep for one candidate family. Your sandbox is read-only, so
you cannot write files: your final message IS the deliverable. The supervisor copies it verbatim
into intent/research/<family>.md, so write it as a complete, self-contained markdown document
with the title on the first line. Do not write anything else before or after the document.

Read first: intent/README.md (selection criteria), intent/research/landscape-2026-10-15.md (the
format and depth expected; do not repeat its content).

## Method

Use live web search for everything. Prefer primary sources: repos, docs, changelogs, papers. For
each tool record stars and last activity as of today with the date; shell commands that need the
network (gh api, curl) may be blocked by the sandbox, so if they fail, take the figures from the
GitHub page via search and mark them "from page". Never invent a figure or a URL; if unknown,
write "not found". Depth over breadth: a few well-checked rows beat many guessed ones.

## Document format

1. Title: "# Landscape sweep: <family>, 2026-10-16 (Codex research job research-prediction-markets-d1)"
2. Method, three lines.
3. One section per sub-area below, each a table: Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family.
4. "Research or practitioner baselines": numbers or write-ups that bound what is achievable, with URLs.
5. "Unoccupied niches": numbered, two lines each, the evidence that it is unoccupied.
6. "Candidate products": two or three, each: one-line pitch; what Codex would build in about
   twelve build days as four to six increments that each ship something verifiable by a command;
   disk and runtime footprint (must be Python with uv or a small Go or JS program, no Docker, no
   datasets, free to run); who uses it; the strongest argument against it.
7. "Sources": every URL used.

Constraints: no emojis, no em dashes, under 220 lines, humble language (say what a page says,
not what is true). Point-in-time counts carry the date. Do not decide for the lab; lay out the
evidence.

## The family

Byron trades on prediction markets (Polymarket mainly; Kalshi and Manifold as context) in small
size from New Zealand, using the public APIs and his own scripts. The family is free, local,
open tooling for one trader: market data, portfolio and risk, calibration, alerting, and
analysis. Trading execution exists already (official clients, py-clob-client) and is not the
gap to look for; look for what is missing around it. Nothing in this family may hold or move
money without Byron; the product may read positions, prices and order books, and may prepare
orders, but placing them is out of scope for the lab.

Sub-areas to sweep:

A. Official and community API clients and CLIs for Polymarket (Gamma, CLOB, data API), Kalshi,
   Manifold: maturity, what they expose (order books, trades, positions, resolution history).
B. Portfolio tracking and P and L for prediction-market positions: realised and unrealised,
   fees, resolution outcomes, export; what exists open source and what the hosted dashboards
   (Polymarket Analytics, Dune dashboards, PolymarketWhales and the like) cover.
C. Calibration and forecasting skill tracking for an individual: Brier score over own trades or
   forecasts, comparison against market close, tools from the forecasting community (Metaculus
   exports, Fatebook, forecasting scorers) and what applies to traded markets.
D. Market scanners and alerting: new markets, price moves, spread or liquidity changes,
   cross-venue divergence (Polymarket vs Kalshi on the same event), resolution approaching;
   open tools, bots, and what they cost to run.
E. Research and analysis: historical price series access (free tiers, rate limits, bulk
   endpoints), event-study tooling, market microstructure write-ups on these venues.

Be explicit about API terms of use, rate limits, authentication needs, geographic restrictions
and whether read access is free; cite the page. For each candidate product, say what a reader
of a daily blog would find interesting about watching it get built and what Byron would use
weekly.
