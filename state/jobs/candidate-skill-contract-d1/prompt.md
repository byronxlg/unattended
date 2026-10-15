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

## The candidate: Skill Contract Check, executable compatibility receipts for agent skills

Sweep: intent/research/agent-skills.md, candidate 1, and sections C and E of that document.

Pitch: a CLI that reads a small contract next to a SKILL.md (which executables, versions, flags,
files and endpoints the skill's instructions assume), probes the local machine, and emits a
receipt bound to the skill bytes and the tool identities, so a skill author or a Skillfold user
can see which documented assumptions still hold before an agent trusts the skill. Byron writes
skills (byronxlg/skills) and distributes them with Skillfold (byronxlg/skillfold); both are
user one.

Settle, with read-only inspection (allowed: the installed skills under ~/.claude/skills and
~/.agents/skills, which are skill text, not sessions; web search for Skillfold, agentlint,
skilllint, driftlint and SkillGuard; not allowed: anything under ~/.codex, ~/.claude/projects,
or other repositories):

- Pick three installed skills that document CLIs (candidates: tts, obsidian, polymarket,
  playwright-cli, dbt). For each, list the executables, flags, files and endpoints its SKILL.md
  assumes, and test which of those assumptions you can check right now with read-only commands
  (command -v, --version, --help, ls). Paste the trimmed output. Say which assumptions a
  contract could express and which it could not.
- Compare with agentlint (Mr-afroverse/agentlint) and driftlint (alifurkangokce/driftlint):
  what they already check, and whether Skill Contract Check is a new tool or a rule set for one
  of them. Be blunt if it is the latter.
- What Skillfold's lockfile and check command already bind (hashes of skill content), and how a
  receipt would reference a Skillfold-pinned revision without modifying Skillfold.
- How a contract stays honest: what a passing receipt does and does not prove, and how the
  product reports that in one line.
