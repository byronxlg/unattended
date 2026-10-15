# Research brief: tooling for authoring, testing and distributing agent skills

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

1. Title: "# Landscape sweep: <family>, 2026-10-16 (Codex research job research-agent-skills-d1)"
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

Byron writes skills for coding agents (Claude Code skills in SKILL.md form, Codex skills,
AGENTS.md and CLAUDE.md rules, hooks) and distributes them to his own machines with a small
manifest-and-lockfile tool he wrote (Skillfold: a manifest, a lockfile, install into
~/.claude/skills, ~/.agents/skills, ~/.claude/rules, and a managed block in ~/.codex/AGENTS.md).
The family is open tooling around skills: lint, test, trigger evaluation, measuring whether a
skill is used and whether it helps, registries and distribution, and drift between a skill and
the tool it documents.

Sub-areas to sweep:

A. Skill formats and specs: Anthropic's SKILL.md and Agent Skills spec, OpenAI Codex skills
   and plugins, agents.md, Cursor rules, Windsurf, Continue; what is interoperable, what is not.
B. Registries and distribution: skills.sh and similar, GitHub topic repos, the Claude Code
   plugin marketplace, Codex plugin directory; install tooling (npx skills, skillfold-like
   tools, dotfile managers); counts and activity.
C. Testing and evaluation of skills: trigger accuracy evals (does the skill activate when it
   should), outcome evals (does the task go better with it), harnesses (Anthropic skill-creator
   evals, promptfoo, inspect, custom runners); what is open and what exists only as blog posts.
D. Observability: which skills activated in which sessions (Claude Code OTel skill_activated
   event, local JSONL transcripts, Codex rollouts), how anyone reports skill usage and outcome.
E. Quality and drift: linters for SKILL.md frontmatter and description length, checks that a
   skill's commands still exist and still run, stale-skill detection, dedup across skills.

Say plainly where Skillfold already occupies the niche, so the lab does not rebuild Byron's own
tool. For each candidate product, say what a reader of a daily blog would find interesting about
watching it get built and how its value could be shown by a command.
