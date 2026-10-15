# Research brief: fleet operations for small live projects from one machine

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

1. Title: "# Landscape sweep: <family>, 2026-10-16 (Codex research job research-fleet-ops-d1)"
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

Byron runs a fleet of about a dozen small live projects (bots, scrapers, static sites, scheduled
jobs, a few web services) from one Mac mini, with launchd and cron, GitHub Actions for deploys,
runbooks as markdown with frontmatter (project, tier, owner, lifecycle, reviewed date), and no
central monitor beyond "the output went stale". The family is tooling that makes operating such
a fleet from one host cheap and trustworthy without a SaaS.

Sub-areas to sweep:

A. Dead-man switches and scheduled-job monitors (healthchecks.io, Cronitor, Dead Man's Snitch,
   self-hosted and local equivalents, launchd-aware tools, cron linting).
B. Runbook-as-code and fleet registries: tools that read a directory of runbooks or service
   manifests and check them (staleness, required fields, owner, tier), or generate status pages.
C. Local-first status and health rollup for a personal fleet: single binary or script that polls
   endpoints, log freshness, process liveness and git-push recency and renders one page or one
   message (Telegram, Slack).
D. Drift between "what should be running" (plists, crontabs, workflow files, IaC) and what is
   (launchctl, ps, gh run list, actual deploy): tools that diff declared versus observed.
E. Operational telemetry over a fleet of GitHub repos: Actions run durations, failure streaks,
   stale dependabot, last deploy per repo, with control-band style alerting (see section D of
   intent/research/landscape-2026-10-15.md for the detector landscape; do not redo it, link it).

For each candidate product, say what Byron would see on day 12 and what a reader of a daily blog
would find interesting about watching it get built.
