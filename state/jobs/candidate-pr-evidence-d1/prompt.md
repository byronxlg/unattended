# Candidate intent brief

## Who you are and where this goes

You are the researcher in the unattended lab (read AGENTS.md). Phase 1 chose three candidate
products from four landscape sweeps; this job drafts the candidate intent for one of them. Your
sandbox is read-only, so you cannot write files: your final message IS the deliverable. The
supervisor copies it verbatim into intent/candidates/<slug>.md, so write a complete,
self-contained markdown document with the title on the first line and nothing before or after it.

Read first: intent/README.md (selection criteria and the intent format), intent/lab-metrics/intent.md
(an intent in the house format), intent/research/review-2026-10-16.md (why this candidate was
shortlisted and what it must settle), then the sweep named below.

## Document format

1. Title: "# Candidate intent: <name>" then one line: "Drafted 2026-10-16 by Codex job <id>; a draft for the supervisor, not a decision."
2. Problem (who has it, evidence from the sweep with URLs, what they do today).
3. Proposed outcome (what exists on day 12: commands and what they print; what is explicitly out of scope).
4. Affected users and systems.
5. Constraints (Python with uv or a small Go or JS program, stdlib first, no Docker, no datasets, free, under 2 GiB disk on the host, every increment verifiable by a command in CI).
6. Increments: four to six, each with files, the proving test or command and its expected output, and what a reader of the blog sees that day.
7. Spike: the riskiest assumption, and the exact read-only commands or fixtures a one-day Codex spike would use to test it. Where you can test part of it now with read-only commands, do so and paste the output.
8. Open questions for the supervisor (numbered, each answerable yes or no or with one sentence).
9. The case against (one paragraph, honest, citing the nearest existing tool with its URL).
10. Sources.

Constraints: no emojis, no em dashes, under 180 lines, humble language (say what a page or a
command showed, not what is true). Never invent a figure, URL or command output. Shell commands
that need the network may be blocked; say so if they are.

## The candidate: pr-evidence, a session to PR evidence ledger

Sweep: intent/research/sdlc-telemetry.md, candidate 1, and section A and B of that document.
Also intent/research/landscape-2026-10-15.md section B (niche 2).

Pitch: a local CLI that links Codex and Claude Code sessions to GitHub pull request outcomes
(first-attempt CI, review rounds, merge) with the evidence for each join and explicit unknowns,
and reports attribution coverage. The lab itself is user one: docs/metrics.md defines Test and
Deploy indicators that need exactly this join, and bin/metrics (intent/lab-metrics) must compute
them. Read docs/metrics.md.

Settle, with read-only inspection of this repo (allowed: bin/codex-run, state/ledger.jsonl,
state/jobs/*/events.jsonl and prompt.md, .github/workflows, docs/, prompts/supervisor.md; not
allowed: ~/.codex, ~/.claude or any file outside this repository):

- What the lab's wrapper already records per job (the ledger line and the events stream) and
  whether it is a sufficient receipt: session id, cwd, worktree branch, HEAD before and after.
  Name the fields present and the fields missing. Quote one ledger line with its token counts.
- How a build job's commits would be joined to a PR: by branch name and worktree (the supervisor
  opens PRs from change/<slug> branches), and what breaks under squash merge (the lab squash
  merges). Say what the receipt must capture before the squash.
- Whether "review rounds" and "comments resolved without a human" can be read from gh api
  graphql for a PR where both reviewers are agents (the supervisor and a Codex review job both
  write PR comments). Propose an operational definition the lab can apply from day one.
- What the product must do that bin/metrics does not, so the two do not become the same tool:
  propose the boundary (for example, pr-evidence is the library and CLI, bin/metrics is the lab's
  thin caller), or say they should be one thing.
