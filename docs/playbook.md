# The AI-native SDLC playbook, condensed

Source: https://claude.com/resources/articles/the-ai-native-sdlc-playbook (Anthropic). This is the
working summary the supervisor follows; `docs/metrics.md` lists the indicators and how this lab
measures them. Thesis: code generation is no longer the constraint, the human-speed steps around
it are; each stage commits an artifact the next stage reads, and together they form the audit
trail. Humans concentrate at the gates. In this lab the "human" at most gates is the supervisor,
with Byron holding only production release authorization; the blog says so.

## Stage 1 Plan: `intent.md`

The originator brainstorms and writes a proto-spec in their own terms: problem, proposed
outcome, affected users and systems, constraints, open questions. Stored version-controlled in
`intent/<slug>/intent.md`. The accept/reject decision is the merge or the close.

## Stage 2 Design: `spec.md`

Requirements and design in one session from the accepted intent, guided by policy skills,
producing `spec.md` with flagged concerns; the product owner reviews but does not write it;
concerns resolved before engineering sees it; committed beside the intent. Accepting the spec
starts plan mode.

## Stage 3 Build: `plan.md`, auto mode, CLAUDE.md, skills, hooks, parallel sessions

Plan mode first (read-only exploration): files to change, order, proving tests; the engineer
interrogates the plan (what breaks, riskiest step, rejected alternatives); the bar is that
someone who never saw the conversation could implement from the plan alone. Committed as
`plan.md`; if implementation departs, `plan.md` is updated in the same commit. Auto mode for
routine work once guardrails exist. `CLAUDE.md` under a page: build, test, lint commands,
conventions, known agent mistakes; a mistake made twice goes in. Skills for knowledge that
must be applied consistently; skills are advisory, policies that must hold need a deterministic
backstop (hook or PR-time review). Hooks: fast, file-scoped at build time; heavy checks at commit
or PR; human approval hooks belong in Deploy. Parallel sessions split by file independence from
the plan; tasks sharing files run sequentially.

## Stage 4 Test: feedback loop, continuous evals

Give the agent a way to verify its own work (single command, non-zero on failure, documented
healthy output), quantifiable targets, done includes showing the verification output. Bug fixes:
failing test first, committed, then fix without editing the test (hook can enforce). An agent
must not weaken checks on its own code. A verifier with fresh context is a distinct final check.
Evals: 20 to 50 real tasks with accepted outcomes, each a prompt plus checks; run on schedule and
on any change to CLAUDE.md, skills or hooks; a pass-rate drop gates the config change; every
production incident adds an eval.

## Stage 5 Deploy: AI in the PR loop, hooks as approval gates, CI/CD

The agent gives and receives reviews. `REVIEW.md` defines the passes (bugs, security, compliance
against spec and plan), Important vs Nit, a nit cap, exclusions. Findings do not approve or
block alone; code owner approval remains; the agent that wrote code cannot approve it. Approval
gates expressed as hooks that allow, ask or block, with a route to approval; blocks explain
themselves. Non-interactive runs in pipelines for judgement steps; all output as PRs through
branch protection; tiered autonomy (dev free, staging between, production prepared by the agent
and authorized by a release manager); rollback the most rehearsed path.

## Stage 6 Maintain: closing the loop, scans, on call

Headless operation triggered by band breach, ticket, message or schedule. Detection is
deterministic: rolling baseline and Western Electric rules, tiers in `bands.yaml` (1 sigma log,
2 sigma diagnose read-only, 3 sigma propose via PR or runbook). Output is an `intent.md` in Stage
1 format; triage decides fix now, schedule or dismiss; dismissals tune the bands; a shipped fix
adds an eval. Recurring scans with findings through the same gates.
