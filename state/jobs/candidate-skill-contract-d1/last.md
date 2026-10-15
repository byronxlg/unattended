# Candidate intent: Skill Contract Check
Drafted 2026-10-16 by Codex job candidate-skill-contract-d1; a draft for the supervisor, not a decision.

## Problem

Byron authors skills and distributes them with Skillfold. A reproducible installation can preserve instructions whose external tools no longer support the documented interface. Today, authors can inspect help manually, discover failures during agent work, or maintain separate tests.

The sweep identified this narrower gap after finding existing distribution, linting and evaluation tools. [Skillfold](https://github.com/byronxlg/skillfold) documents content pinning and installation checks. [agentlint](https://github.com/Mr-afroverse/agentlint) documents instruction consistency checks. [SkillGuard](https://arxiv.org/html/2605.10990v1) already frames environmental drift as contract violation. This candidate proposes a small implementation, not a new research concept.

Read-only inspection found two installed skills whose primary commands were absent from this process's PATH. A third skill's help command returned exit 0 despite failing to print help under the sandbox. These observations support explicit environment checks; they do not establish failures in Byron's normal interactive environment.

### Three installed skills inspected

**tts**, from `~/.claude/skills/tts/SKILL.md`:

- Executables: `scripts/say.sh`, Bash, Doppler, `ffmpeg` for joining audio, `jq`, `curl`, `tee`, `base64`, `afinfo` and `grep`. No general minimum versions are declared; the text explicitly discusses macOS Bash 3.2.
- Interfaces: helper `--help`, `--text`, `--voice`, `--speed`, `--tone`, `--open`, `--compare`, `--name`, `--ladder`, `--file`, `--split`; `doppler run`; `jq -n --arg` and `-r`; `curl -s -H -d`; `base64 -d`.
- Files: bundled `scripts/say.sh`; caller-supplied `script.txt`; output directory `~/Downloads/tts`; example outputs `/tmp/res.json` and `out.mp3`. Outputs are not prerequisites.
- Endpoints: `https://api.openai.com/v1/chat/completions`; the helper source supplies `https://api.openai.com/v1/audio/speech`. Authentication assumes Doppler `global/home` and `OPENAI_API_KEY`.
- Expressible: executable/file presence, helper and interpreter hashes, help-output assertions, declared input ranges, endpoint identity. Not established by these probes: credentials, accepted models or voices, generated-audio quality, transcript fidelity, or the skill's empirical claims about pace and tone.

**dbt**, from `~/.agents/skills/dbt/SKILL.md`:

- Executables: `dbt`; `jq` appears in `allowed-tools`. No version requirement is stated.
- Interfaces: `dbt show`, `dbt clone`, `--limit`, `--defer`, `--state`, `--select`. Contracts must associate flags with the relevant subcommand rather than search one global help page.
- Files: seven bundled reference guides; project model YAML documents; caller-selected production artifact directory. No concrete warehouse profile or project path is supplied.
- Endpoints: `hub.getdbt.com` for package discovery; an unspecified warehouse. The linked dbt documentation URL is a reference, not an operational dependency.
- Expressible: command discovery, subcommand help, references, selected project files and artifact paths. Not established: warehouse access, adapter compatibility, correctness of SQL, business meaning, or whether a new model is justified.

**playwright-cli**, from `~/.agents/skills/playwright-cli/SKILL.md`:

- Executables: `playwright-cli`; fallback `npx playwright cli`; `npm` for installation; `jq` and `diff` in examples. Browser engines are runtime dependencies. No minimum version is stated.
- Interfaces include navigation, interaction, snapshots, storage, routing and tracing. Documented options include `--submit`, `--path`, `--data`, `--regex`, `--filename`, `--hires`, `--domain`, `--httpOnly`, `--secure`, `--status`, `--body`, `--description`, `--duration`, `--position`, `--annotate`, `--raw`, `--style`, `--hide`, `--json`, `--browser`, `--mobile`, `--device`, `--persistent`, `--profile`, `--extension`, `--cdp`, `--config`, `--depth`, `--boxes`, and `-s`. Installation examples use `npx --no-install playwright --version` and `npm install -g`.
- Files: nine bundled references; optional config, browser profile, upload files, storage-state JSON and scripts; generated snapshots under `.playwright-cli/`. Example filenames are caller choices.
- Endpoints: caller-selected websites; optional CDP at `http://localhost:9222`. `example.com`, `api.example.com` and the tutorial visit to `playwright.dev` must not become mandatory health checks.
- Expressible: command alternatives, individual subcommand/flag contracts, selected files and optional endpoint checks. Not established: browser launch, extension connectivity, selector correctness, session permissions or successful page interactions.

### Existing tools and the product boundary

| Tool | Documented coverage | Implication |
| --- | --- | --- |
| [Mr-afroverse/agentlint](https://github.com/Mr-afroverse/agentlint) | References, dispatch coverage, duplicate names/content, trigger overlap, contradictions, dates, source constants, configured JSON/YAML ground truth and deprecated patterns. Behavioral testing is a prompt sheet. | Static missing-file and documented-version checks already belong here. Its inspected documentation did not describe local argv probes or receipts invalidated by executable changes. |
| [driftlint](https://github.com/alifurkangokce/driftlint) | Missing paths/imports/config references, removed npm scripts and Make targets, instruction twins, loading budgets and reviewed memory; optional model-assisted narrative checks. | Its `dead-command` rule is not a general external-CLI flag probe. Its existing rules cover much of any proposed static checker. |
| [bueti/skilllint](https://github.com/bueti/skilllint) | Metadata, description/body heuristics, referenced resources and orphaned files; custom Go rules are supported. | Another package-validity linter is unnecessary. |
| [SkillGuard](https://arxiv.org/html/2605.10990v1) | Extracts operational contracts, separates them from incidental mentions, validates available evidence and localizes repairs. | The conceptual approach already exists. This search did not locate a runnable public implementation; the paper describes an anonymized artifact and later public release. |

**Judgment:** presence checks and static assertions alone would be an agentlint rule set. A separate executable is defensible only for the probe runner, evidence identity and stale-receipt lifecycle. That is additional machinery beyond the inspected configurations, although it could still be implemented upstream. Do not build a general skill linter.

## Proposed outcome

By day 12, `skillcheck` reads an author-written `contract.toml` beside `SKILL.md`, runs selected local compatibility probes, and emits text or JSON evidence. Each assertion names its source line, operational purpose, prerequisites and expected result. Examples and optional features are explicitly distinguished from requirements.

The following are proposed acceptance interfaces and expected output, not commands implemented or run today. Commands run from `product/skill-contract-check/`:

```text
uv run skillcheck validate examples/tts
VALID examples/tts/contract.toml

uv run skillcheck check examples/removed-flag
FAIL cli.flag: --speed absent from declared help output

uv run skillcheck check examples/compatible --format json
JSON receipt containing skill, contract, tool identities and per-probe evidence

uv run skillcheck verify-receipt examples/receipt.json --skill examples/changed-tool
STALE tool identity changed; rerun probes
```

Exit codes: 0 for all required assertions passing; 1 for a demonstrated mismatch; 2 for invalid input or incomplete evidence; 3 for stale receipts. Missing optional tools produce explicit skips. A blocked required probe cannot produce an overall pass.

The passing summary is one line: **`PASS declared probes only; task correctness, safety and undeclared assumptions are unverified.`**

A receipt records skill/resource and contract hashes; resolved executable paths and hashes; declared interpreters or module entrypoints; observed version output; OS/architecture; probe argv, working-directory context, timestamp, exit status and bounded evidence. It records identity before and after probing and rejects changes during the run. Unidentified transitive dependencies remain a stated limitation.

Receipt verification means the recorded identities still match, not that yesterday's remote observation remains true. Remote checks require a new observation. Receipts are unsigned local evidence, not attestations of author identity or resistance to forgery.

Out of scope: automatic execution of Markdown code blocks, model-based contract extraction, skill installation, repair, trigger evaluation, task-quality scoring, credential validation, paid API calls, browser sessions and warehouse queries.

### Referencing Skillfold without changing it

Skillfold's documented lock entries contain `source`, remote `resolved` revision/version and `integrity`. Local sources are unpinned. Supporting files participate in content integrity; installed names can be rewritten and compositions generated, so a raw `SKILL.md` digest is not interchangeable with the lock integrity value. Its `@installed` mode already follows installed npm package versions. [Manifest reference](https://github.com/byronxlg/skillfold/blob/main/docs/manifest.md)

`skillfold check` documents offline agreement between manifest, lock and installed files, including remote hashes, local-source equality, compositions and `@installed` versions. It does not document executing the skill's external tools. [CLI reference](https://raw.githubusercontent.com/byronxlg/skillfold/main/docs/cli.md)

The adapter will read an explicitly supplied lockfile, recording its digest, schema version, entry name, `source`, `resolved`, `integrity` and selected target alongside independently measured installed bytes. Mere inclusion of a pin is labelled `referenced`, not `verified`. Verification requires a matching Skillfold check observation, with unchanged inputs around that check. Unsupported schema or unavailable check evidence remains unknown. Local entries get no invented revision.

Receipts live outside installed skill directories, avoiding changes to content being hashed. No Skillfold patch, install or update is required. The global lock and global check were deliberately not inspected here because they can traverse locations outside this brief.

## Affected users and systems

User one is Byron as author and Skillfold consumer. Other users are maintainers reviewing skill changes and CI jobs checking declared dependencies. Inputs are selected skill directories, optional lockfiles and trusted local tools. Outputs are receipts and command failures. Existing installations and source skills remain unchanged by checking.

## Constraints

- Python 3.11+ with uv; stdlib for TOML, hashing, subprocesses and JSON. Permit one small YAML dependency for Skillfold lockfiles.
- Free offline core; no Docker, datasets, model calls, browser downloads or warehouse adapters. Development and caches must fit within the host's available disk, under 2 GiB.
- Every increment has an offline proving command usable in CI. Live-service observations are optional and never acceptance prerequisites.
- Execute only explicitly selected, reviewed probes as argv arrays, without a shell; bound runtime and output. Do not inherit credentials by default.
- `--help` is not a security boundary. Production probes require trusted executables; subprocess limits do not make arbitrary code read-only.
- Version assertions use author-declared requirements. Record unspecified versions without inventing a compatibility range.
- Contracts cannot prove their own completeness. Report declared coverage and explicit unknowns without a health score.

## Increments

All paths below are relative to `product/skill-contract-check/`. Outputs are acceptance targets.

| Days | Files and shipped behavior | Proving command and expected result | Blog evidence |
| --- | --- | --- | --- |
| 1-2 | `pyproject.toml`, `skillcheck/schema.py`, `examples/*/contract.toml`, `tests/test_schema.py`: schema, source references, required/optional roles and rejection of shell commands. | `uv run python -m unittest discover -s tests -p test_schema.py`; ends `OK`, including invalid-contract cases. | Day 1 inventories the three skills; day 2 contrasts an operational prerequisite with an example URL. |
| 3-4 | `skillcheck/local.py`, `tests/test_local.py`, `fixtures/tools/`: executable resolution, version predicates and file checks. | `uv run python -m unittest discover -s tests -p test_local.py`; ends `OK`, covering missing PATH entries, alternatives and optional dependencies. | Day 3 shows the absent dbt command; day 4 shows why an absent global Playwright command does not rule out its fallback. |
| 5-7 | `skillcheck/probes.py`, `tests/test_probes.py`, `fixtures/probes/`: bounded trusted argv probes, output assertions, explicit unknowns; optional unauthenticated HTTP checks tested against loopback fixtures. | `uv run python -m unittest discover -s tests -p test_probes.py`; ends `OK`, covering removed flags, exit-0/empty-output, timeout and blocked endpoint cases. | Day 5 reproduces the help failure; day 6 catches a removed flag; day 7 shows help coverage passing while behavior remains untested. |
| 8-9 | `skillcheck/receipt.py`, `tests/test_receipt.py`, `fixtures/receipts/`: identity binding and stale-evidence rejection. | `uv run python -m unittest discover -s tests -p test_receipt.py`; ends `OK` after separately changing skill, helper, contract, interpreter and executable bytes. | Day 8 changes a tool without changing its version string; day 9 shows why an unchanged version is insufficient. |
| 10-12 | `skillcheck/skillfold.py`, `skillcheck/report.py`, `fixtures/skillfold/`, `tests/test_acceptance.py`, `README.md`: lock references, text/JSON reports and complete offline demonstrations. | `uv run python -m unittest discover -s tests`; ends `OK`, including local/unpinned, renamed, composed and unsupported-lock cases. | Day 10 joins a pin to evidence; day 11 compares two fixture environments; day 12 publishes the limitations and measured footprint. |

## Spike

**Riskiest assumption:** a short author-maintained contract catches useful compatibility failures beyond existing lint without turning incidental examples or sandbox restrictions into claims that a skill is broken.

The one-day spike uses the three installed texts and their bundled resources only. Commands already run below are read-only in intent; the help command encountered a sandbox-denied temporary-file attempt. Output is trimmed, with omissions identified.

```text
$ command -v dbt; printf 'dbt lookup exit=%s\n' "$?"
dbt lookup exit=1
$ command -v playwright-cli; printf 'playwright-cli lookup exit=%s\n' "$?"
playwright-cli lookup exit=1
$ command -v npx npm jq doppler ffmpeg
/opt/homebrew/bin/npx
/opt/homebrew/bin/npm
/opt/homebrew/bin/jq
/opt/homebrew/bin/doppler
/opt/homebrew/bin/ffmpeg
$ /bin/bash --version | head -n 1
GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
$ jq --version
jq-1.8.1
$ ffmpeg -version | head -n 1
ffmpeg version 8.1.2 Copyright (c) 2000-2026 the FFmpeg developers
$ ~/.claude/skills/tts/scripts/say.sh --help; printf 'say.sh help exit=%s\n' "$?"
/Users/byron/.claude/skills/tts/scripts/say.sh: line 26: cannot create temp file for here document: Operation not permitted
say.sh help exit=0
$ skillfold --version
2.7.0
```

The executable lookups were performed in a larger loop; the displayed subset preserves their output. Additional help probes showed the following selected lines:

```text
$ doppler run --help
  -c, --config string                     config (e.g. dev)
  -p, --project string                    project (e.g. backend)
$ jq --help
  -n, --null-input          use `null` as the single input value;
  -r, --raw-output          output strings without escapes and quotes;
      --arg name value      set $name to the string value;
$ curl --help all
 -d, --data <data>                   HTTP POST data
 -H, --header <header/@file>         Pass custom header(s) to server
 -s, --silent                        Silent mode
$ base64 --help
  -D, -d, --decode  decode input
```

`ls` found the helper and all seven dbt and nine Playwright reference files named by their respective skills. Selected output:

```text
$ ls ~/.claude/skills/tts/scripts/say.sh
/Users/byron/.claude/skills/tts/scripts/say.sh
$ ls ~/.agents/skills/dbt/references
debugging-dbt-errors.md
discovering-data.md
evaluating-impact-of-a-dbt-model-change.md
managing-packages.md
planning-dbt-models.md
writing-data-tests.md
writing-documentation.md
$ ls ~/.agents/skills/playwright-cli/references
element-attributes.md
playwright-tests.md
request-mocking.md
running-code.md
session-management.md
storage-state.md
test-generation.md
tracing.md
video-recording.md
```

The helper source handles `--help` before credentials or rendering, but its Bash heredoc failed here and an explicit `exit 0` masked that failure. Record `UNKNOWN sandbox blocked help output`, not an unsupported-flag finding. The dbt and Playwright checks establish missing global commands only. Their version/help probes could not run; the npm fallback was not invoked because it may access caches or attempt writes. No credentials, service requests, browser sessions or warehouse operations were exercised. Web retrieval worked; no shell network request was attempted.

For the remaining spike, specify tiny fixtures: a compatible CLI advertising `--speed`; one removing it; one advertising it but rejecting actual use; one returning empty stdout and exit 0; one timing out; and two different executables with identical version output. Add lock fixtures for remote pins, local sources, aliases and compositions. These fixtures were not created or executed in this read-only job.

The proving command after fixture implementation is `uv run python -m unittest discover -s tests -p test_spike.py`, expected to end `OK`. It must assert that missing evidence never passes, examples create no probes, tool-byte changes invalidate receipts, and advertised flags do not imply behavioral compatibility.

Proceed only if the spike demonstrates useful probe results beyond static lint and the supervisor accepts the authoring burden. Otherwise reduce this to agentlint rules plus ordinary helper-script tests.

## Open questions for the supervisor

1. Is a standalone probe-and-receipt runner worth maintaining if its static checks duplicate agentlint?
2. Are these three skills acceptable initial examples despite two primary commands being absent from the research PATH?
3. Should version one leave every authenticated endpoint assumption explicitly unverified?
4. May the implementation add one small YAML dependency for Skillfold lock parsing?
5. Will Byron maintain contracts alongside source skills rather than edit generated installed copies?

## The case against

[agentlint](https://github.com/Mr-afroverse/agentlint) is the nearest practical alternative: extend its checks and use ordinary tests for helper behavior. Contracts duplicate instructions, require maintenance, and may reward easy assertions while leaving the consequential assumptions untested. This inspection found missing commands and a sandbox-specific help failure, not a demonstrated production regression. SkillGuard already supplies the conceptual framing, while Skillfold's package-following mode reduces some version drift. Unless identity-bound receipts prove useful in the spike, a separate twelve-day product would add packaging and terminology around a small test suite.

## Sources

- Local selection context: `intent/README.md`, `intent/lab-metrics/intent.md`, `intent/research/review-2026-10-16.md`, and `intent/research/agent-skills.md`, especially sections C, E and candidate 1.
- Installed primary evidence: `~/.claude/skills/tts/SKILL.md`, its `scripts/say.sh`, `~/.agents/skills/dbt/SKILL.md`, and `~/.agents/skills/playwright-cli/SKILL.md`; inspected 2026-10-16.
- Tool comparisons: [agentlint](https://github.com/Mr-afroverse/agentlint), [driftlint](https://github.com/alifurkangokce/driftlint), [skilllint](https://github.com/bueti/skilllint), [SkillGuard paper](https://arxiv.org/html/2605.10990v1).
- Distribution contract: [Skillfold](https://github.com/byronxlg/skillfold), [manifest reference](https://github.com/byronxlg/skillfold/blob/main/docs/manifest.md), [CLI reference](https://raw.githubusercontent.com/byronxlg/skillfold/main/docs/cli.md). Web observations are documentation claims retrieved on 2026-10-16, not executed competitor evaluations.