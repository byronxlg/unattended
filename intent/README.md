# intent/

One directory per change, named by slug: `intent.md` (Plan stage, written by the originator),
`spec.md` (Design stage, written by the agent and accepted by the product owner), `plan.md`
(Build stage, from plan mode, checklist of steps kept in sync with the implementation). The git
history of these files is the Plan and Design indicators in `docs/metrics.md`.

## Phase 1 research briefs (days 1 to 3)

The product is chosen here, not before. Two kinds of Codex research jobs, read-only, plus the
supervisor's own judgement:

1. Landscape sweeps: for each candidate family, what exists, how mature, what is missing, with
   URLs. Output into `intent/research/<family>.md`.
2. Candidate intents: for the three strongest candidates, a draft `intent.md` in the playbook's
   format (problem, proposed outcome, affected users and systems, constraints, open questions),
   plus a one-paragraph case against it. Output into `intent/candidates/<slug>.md`.

Selection criteria (from the brief and the host's limits): buildable by Codex in about twelve
build days in increments that each ship; verifiable by commands; small on disk (under 2 GiB
free on the host, so Python with uv or a small compiled program, no Docker, no datasets);
free to run; useful to Byron or to people like him (he runs a fleet of small live projects from
one Mac, trades on prediction markets, writes skills for agents, cares about operations and
measurement); interesting enough that twenty days of posts about it are worth reading. The
decision and its reasons are recorded in `intent/<slug>/intent.md` and in the day's post.
