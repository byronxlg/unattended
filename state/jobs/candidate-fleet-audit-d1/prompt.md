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

## The candidate: Fleet Audit, declared versus observed jobs on one Mac

Sweep: intent/research/fleet-ops.md, candidate 2, and sections A and D of that document.

Pitch: a read-only CLI that reads a registry of a dozen projects (a directory of markdown runbooks
with frontmatter: project, tier, owner, lifecycle, reviewed date, and the launchd label or cron
line each project should run under), observes launchd and cron on the host, and reports per
project: declared but not loaded, loaded but disabled, wrong executable or working directory,
last exit status, legitimately idle, and no recent output. With "cannot determine" as a first
class state. This lab's own loop (bin/tick, launchd label com.unattended.tick) is user one.

Settle, with read-only commands on this host (macOS 26.5; allowed: launchctl list, launchctl
print gui/$(id -u) and launchctl print gui/$(id -u)/<label>, crontab -l, ls and plutil -p on
~/Library/LaunchAgents/*.plist, cat of the lab's own .plist and bin/tick; do not read any other
repository's contents or anything under ~/.codex or ~/.claude). Paste the real output, trimmed,
redacting nothing but noting any path you redact:

- What launchctl list and launchctl print emit for the lab's label and for one third-party
  label; which fields are machine-readable (pid, last exit status, run count, state, program
  arguments, working directory, calendar interval) and which need parsing of free text. Say
  whether the format looks stable enough to pin fixtures to a macOS version.
- Whether a disabled agent, a never-loaded plist and a loaded-but-idle calendar job are
  distinguishable from these outputs alone, and what evidence (receipt file, log mtime, output
  freshness) the product must ask the project for when they are not.
- What a runbook's frontmatter must declare to make the join unambiguous (label, plist path,
  expected program, expected interval, output path and max age).
- Whether the existing tools LaunchInspector (vincentbattez/launchs-and-crons-inspector) and
  Drift (sunkencity999/drift) could be consumed instead of reimplementing observation; read their
  READMEs with web search and say what their JSON output lacks.
