# Plan brief: Fleet Audit (Build stage, plan mode)

You are the engineer in the unattended lab (read AGENTS.md). Phase 2 accepted the spec; this
job writes plan.md. Your sandbox is read-only: your final message IS the deliverable. The
supervisor copies it verbatim into intent/fleet-audit/plan.md, so write one complete markdown
document, title on the first line, nothing before or after it, under 300 lines. Write for an
engineer who never saw this conversation and will implement from the plan alone, one increment
per job, in a fresh context each time.

Read first, in this order: intent/fleet-audit/intent.md, intent/fleet-audit/spec.md (the body
is the spec; the "Supervisor decisions" section at the end overrides the body where they
differ, read every decision), intent/fleet-audit/evidence/print-disabled-gui501-2026-10-16.txt,
the spike code in .worktrees/spike-fleet-audit/spike/ (launchctl_parse.py, audit.py,
test_audit.py, fixtures/), docs/playbook.md Stage 3, REVIEW.md, and bin/lint (what CI
enforces). Do not run launchctl; do not write files.

## What the plan must contain

1. Package layout under product/fleet_audit/: every file with one line on its responsibility,
   pyproject.toml contents (name, Python 3.12, PyYAML pinned, `fleet-audit` script entry,
   pytest config), and how `uv run fleet-audit` and `uv run python -m fleet_audit.acceptance`
   resolve. Note what CI must run (the five proving commands, pytest, bin/lint) and the
   .github/workflows change needed, if any, as its own small step.
2. Module boundaries: registry (frontmatter, schema, plist join), plist reading, launchctl
   collection and parsing, overrides, output and receipt observation, verdict engine, drift,
   reports (text, JSON), CLI, fixture capture and replay. For each: public functions with
   signatures, the record types they exchange (dataclasses; name the fields), and which spec
   section each implements.
3. Increment order, five increments as the intent lists them, each a separate PR on branch
   change/fleet-audit-<n>. Per increment: files created or changed, the tests that prove it
   (name each test function and what it asserts), the fixtures it freezes (name each real
   record from the spike and each labelled synthetic one), the proving command and its exact
   expected healthy line, and the definition of done. Increment 1 must be buildable with no
   launchctl code at all. The first test of increment 2 is the empty-inventory rule (launchctl
   list exit 1, empty streams: every job cannot_determine with rc=1 in the reason, never an
   empty fleet).
4. Verdict engine design: how the 14 rules become code without the order being implicit (a
   table-driven list of predicates, or equivalent), how `unknown never satisfies a predicate`
   is enforced by type, and the boundary tests A=-1, M, M+1, M+G, M+G+1 by name.
5. Receipt reader: bounded tail read, final-line rule, concurrent-modification detection, the
   ticks_jsonl version 1 producer contract from supervisor decision 4 (completed, failed,
   unestablished) with one test per branch, using real lines from state/ticks.jsonl as
   fixtures (name which lines by their ts).
6. Snapshot format: the manifest and directory layout from the spec, how a live capture is
   written (a `capture` subcommand or a module function the supervisor runs once), and how
   replay refuses live collection.
7. Risks and rejected alternatives: the riskiest step and why, what breaks if launchctl output
   differs on another macOS, three alternatives you rejected with a sentence each.
8. Size: estimated lines per increment and the install footprint of PyYAML under uv (state
   the number if you know it, otherwise say not measured).

## Constraints

Stdlib plus PyYAML only. Read-only product. No implementation code in the plan beyond
signatures, record field lists and test names. Every path absolute and literal as the spec
says. No emojis, no em dashes. Humble: say "not shown" where evidence does not reach.
