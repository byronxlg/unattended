# Research brief: SDLC telemetry for agent-written code, feasibility pass

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

1. Title: "# Landscape sweep: <family>, 2026-10-16 (Codex research job research-sdlc-telemetry-d1)"
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

intent/research/landscape-2026-10-15.md already maps this family (sections A to E) and names
five unoccupied niches. Do not redo the map. This job tests feasibility and freshness of niches
2 and 4 from that note, and checks for anything launched since that note that occupies them:

Niche 2: joining local agent sessions (Claude Code JSONL under ~/.claude/projects, Codex rollouts
under ~/.codex/sessions) to PR outcomes on GitHub (first-pass CI, review rounds, comments
resolved without a human, plan followed).

Niche 4: a small CLI that takes JSONL or CSV telemetry plus a bands.yaml (rolling baseline,
Western Electric or Nelson rules, tiers) and emits a tiered verdict and an issue or message.

Sub-areas:

A. Data availability for niche 2: from the public docs and the openai/codex and Claude Code
   documentation, which fields identify a session, its repo, its branch, its commits and its
   model; which fields are stable or documented versus incidental; what the published schemas
   say. Cite the docs and source files. Do not read Byron's own session files.
B. GitHub side: which gh api or GraphQL fields give check-run outcomes per commit, review
   threads and their resolution, co-author trailers, and PR to branch to commit mapping; rate
   limits for a personal token; anything the Copilot or Claude GitHub apps already label.
C. Fresh entrants since 2026-10-01 in either niche (search GitHub, Hacker News, Product Hunt,
   vendor changelogs): name, what it does, whether it closes the gap.
D. Niche 4 freshness: libraries and CLIs for control charts in Python, Go and JS, with last
   activity; what a bands.yaml would need to express; prior art for GitHub-issue or chat output
   from a detector.
E. Who would use either product besides this lab: teams running Codex or Claude Code in CI,
   solo developers, the ai-native-sdlc template authors named in the earlier note.

For each candidate product, state the riskiest assumption (for example, that Codex rollouts carry
a stable repo and branch identifier) and how a one-day Codex spike could test it.
