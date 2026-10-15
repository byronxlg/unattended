# Landscape sweep: SDLC telemetry for agent-written code, 2026-10-16 (Codex research job research-sdlc-telemetry-d1)

## Method

Read the selection criteria and previous sweep; searched live GitHub, vendor documentation, Hacker News and Product Hunt, then inspected public schemas and source.
All star counts below are **2026-10-16 observations, from page**, including GitHub’s rounding; `gh api` failed with `error connecting to api.github.com`, so unavailable push timestamps are marked “not found.”
This is source inspection, not runtime validation: no files changed, no personal session files inspected; proposed commands and footprint budgets remain unverified.

## A. Data availability for niche 2

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
|---|---|---|---|---|
| [OpenAI Codex](https://github.com/openai/codex) | 129.3k; push not found. [Release activity](https://github.com/openai/codex/releases): 2026-10-14. | The current [rollout protocol](https://raw.githubusercontent.com/openai/codex/main/codex-rs/protocol/src/protocol.rs) defines `SessionMeta.id`, root `session_id`, fork/parent IDs, `cwd`, `cli_version`, `model_provider`; optional `git.commit_hash`, `git.branch`, `git.repository_url`. `TurnContextItem.model` supplies per-turn configuration. | Apache-2.0; inspecting existing logs is free. Generating sessions requires model access. | Git metadata describes a captured state, not a ledger of commits produced. Optional fields, forks and schema evolution require versioned adapters. |
| Codex published app-server schema | Same repository and snapshot. | [`Thread`](https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript/v2/Thread.ts) exposes `id`, `sessionId`, `cwd`, `cliVersion`, nullable `gitInfo`; [`GitInfo`](https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript/v2/GitInfo.ts) uses `sha`, `branch`, `originUrl`. | Published generated types; no additional service required for local use. | `path` is explicitly unstable. `model` explicitly is not per-turn execution telemetry. `projectId` is an application project assignment, not a GitHub repository ID. |
| [Claude Code](https://github.com/anthropics/claude-code) hooks | 150.9k; push not found. [Release activity](https://github.com/anthropics/claude-code/releases): v2.1.300, 2026-10-14. | [Documented hooks](https://code.claude.com/docs/en/hooks) supply `session_id`, `transcript_path`, `cwd`; `SessionStart` includes `model`. | Public documentation and issue repository; Claude Code runtime is commercial. Reading existing hook records is free. | These are documented hook contracts, not a complete, versioned on-disk transcript schema. Common fields do not establish repository remote or output commits. |
| [Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python) session reader | 8.3k; push and dated latest activity not found. | Official [session-browser cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-05-building-a-session-browser) documents `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` and local reading APIs. [`SDKSessionInfo`](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/types.py) includes UUID `session_id`, optional `cwd`, `git_branch`, timestamps. | MIT SDK. The documented read APIs need no model call. | `git_branch` is documented as the branch **at the end** of a session. It is not a branch history or commit attribution record. |

**What is documented versus incidental.** Codex publishes useful protocol types, but that does not establish an immutable archival format. The [recorder implementation](https://github.com/openai/codex/blob/main/codex-rs/rollout/src/recorder.rs) and protocol source are implementation evidence; pin parser fixtures to observed CLI versions. `codex exec --json` is a separately documented [event stream](https://learn.chatgpt.com/docs/non-interactive-mode), with `thread.started.thread_id`, turn events and usage. Do not parse it as if it were a rollout.

For Claude, the SDK offers a stronger integration surface than reverse-engineering every JSONL record. Its [reader implementation](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/_internal/sessions.py) extracts raw `gitBranch` from tail/head records and derives `cwd` where necessary. `SessionMessage.message` exposes a raw API message; observed `message.model` is useful evidence, but not a guaranteed session-wide model. Model switches require message- or turn-level attribution.

**Feasibility boundary.** Session identity and model configuration are available; reliable output-commit identity is the missing link. Capture an explicit receipt containing session ID, canonical repository identity, worktree, before/after HEAD, timestamp and agent version. Historical branch/time matches should remain labelled heuristics. Squashes, rebases, reused branches and several agents sharing a worktree prevent a universal deterministic retrospective join.

## B. GitHub side

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
|---|---|---|---|---|
| GitHub REST checks and Actions | N/A; hosted API. | [Check runs](https://docs.github.com/en/rest/checks/runs): `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`, including `head_sha`, `name`, `app`, `status`, `conclusion`, timestamps. [Workflow runs](https://docs.github.com/en/rest/actions/workflow-runs): `head_sha`, `head_branch`, `event`, `run_attempt`, `workflow_id`; individual attempts are retrievable. | Documented API; authenticated reads require permissions, not a separate analytics subscription. | Latest successful checks can conceal earlier failures. Define workflow set, commit and attempt before calculating first-pass CI. |
| GitHub REST PR and commit mapping | N/A; hosted API. | [PRs](https://docs.github.com/en/rest/pulls/pulls) expose `head.ref`, `head.sha`, `head.repo`, corresponding base fields and `merge_commit_sha`; `/pulls/{number}/commits` lists commits. [Commit endpoints](https://docs.github.com/en/rest/commits/commits) expose messages and associated PRs. | Public repositories readable publicly; private repositories require access. | A branch name alone is not unique across forks. Squash-merge SHA differs from original commits; a current PR head does not preserve every historical push. |
| GitHub GraphQL reviews | N/A; hosted API. | [Pull-request types](https://docs.github.com/en/graphql/reference/pulls) expose reviews with author, state, submitted time and commit; review threads include `id`, `isResolved`, `isOutdated`, comments and nullable `resolvedBy`. | Documented API; paginate connections. | A resolver is not necessarily the person or agent that fixed the code. “Review round” needs an explicit operational definition. |
| GitHub commit authorship | N/A; hosted API. | [Commit GraphQL fields](https://docs.github.com/en/graphql/reference/commits) include `oid`, `message`, `authors`, associated PRs and `statusCheckRollup`. `authors` includes co-authors parsed from trailers. | Existing Git data; free to inspect. | Trailers are editable declarations. Their absence does not establish human authorship; their presence does not identify a local session. |
| Copilot cloud agent | N/A; service. | GitHub’s [security documentation](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/risks-and-mitigations) describes commits authored by Copilot with the assigning human as co-author. | Commercial service; existing commit metadata remains inspectable. | Useful positive attribution signal, but no generic Codex/Claude session mapping or proof of autonomous resolution. |
| Claude Code GitHub-linked analytics | Same Claude Code repository snapshot above; service activity date not found. | [Analytics documentation](https://code.claude.com/docs/en/analytics) describes GitHub-linked “PRs with CC” classification and contribution reporting. | Team/Enterprise feature with organizational setup. | Already occupies aggregate adoption-to-PR reporting. A persistent GitHub label carrying this classification was not verified; detailed local session-to-outcome evidence remains distinct. |

**Collection contract.** Use `gh api` for REST and `gh api graphql` for connections. Preserve raw IDs, SHAs, workflow IDs, attempts and collection timestamps. First-pass CI should mean an explicitly selected initial attempt on an explicitly selected revision, with `unknown` for missing history. Include legacy commit statuses where relevant; do not silently treat an absent check as passing.

A defensible review-round metric could count changes-requested reviews followed by a new revision, while reporting ordinary comments separately. “Resolved without a human” requires an instrumented actor/action record beyond thread state. “Plan followed” requires a versioned plan and explicit checks or a recorded judgment; GitHub has no general field for it.

**Personal-token limits.** GitHub documents a usual REST allowance of **5,000 requests/hour** and GraphQL allowance of **5,000 points/hour**, shared at user level rather than multiplied by tokens. `GITHUB_TOKEN` normally receives **1,000 REST requests/hour/repository**. Secondary limits also apply; cache immutable commit data, paginate, and honor retry responses. Sources: [REST limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [GraphQL limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api).

## C. Fresh entrants since 2026-10-01

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
|---|---|---|---|---|
| [Mixpanel Agent Intelligence](https://mixpanel.com/blog/mixpanel-agent-intelligence/) | N/A; announcement dated **2026-10-01**, updated 10-02. | Advertises conversation analytics connected to agent and business outcomes. | Hosted commercial product; announcement-specific price not found. | Adjacent outcome analytics. The announcement does not establish a local coding-session-to-GitHub adapter or portable SPC CLI. |
| [Pinrail](https://github.com/forgeplane/pinrail) | 41; push not found. [Show HN](https://news.ycombinator.com/item?id=49995778) displayed “6 days ago” when accessed 2026-10-16; exact launch date not found. | Local review inbox; agents submit structured proposals, receive human decisions and can submit revised rounds. | Apache-2.0; free local desktop application. | Relevant new adjacent discovery: captures human intervention explicitly. Author says it does not know the repository; no automatic PR-outcome join or control-chart detector established. |
| [Opaline CLI](https://github.com/opalinehq/cli) | 305; push not found. [Product Hunt](https://www.producthunt.com/products/rudel?launch=opaline) lists **2026-09-24**, outside the window. | Syncs Claude Code and Codex sessions into a team workspace with repository, conversation, model, token and cost context. | MIT CLI; hosted-service price not found. | Cross-agent session analytics is occupied. The inspected description does not establish the requested CI/review/plan outcome join. |
| `bashebr/ai-native-sdlc` detector | 80; push not found. [Changelog](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/CHANGELOG.md) lists detector under **Unreleased**; dated v0.1.0 is 2026-08-21. | Existing source implements a bands-driven detector, detailed below. | MIT; local execution. | Material correction to the previous sweep’s “config-only” description. No evidence establishes that this implementation first appeared after October 1 or October 15. |

Date-filtered GitHub, Hacker News and Product Hunt searches, plus vendor releases, produced **no verified direct entrant launched on October 15-16 that closes either full niche**. This is a search result, not proof of absence. Relative crawl timestamps were not treated as launch dates; Pinrail’s timing remains provisional.

## D. Niche 4 freshness and implementation requirements

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
|---|---|---|---|---|
| [bashebr/ai-native-sdlc](https://github.com/bashebr/ai-native-sdlc) | 80; push not found; dated/unreleased activity above. | [`detect_bands.py`](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/skills/ai-native-sdlc/scripts/detect_bands.py) accepts CSV or JSON arrays and emits tiered JSONL incidents with action/routing metadata. | MIT; Python and YAML dependency; no required service. | Already overlaps the core pitch. Inspection shows current observations included in their own baseline, positive-z threshold checks, and no delivery implementation. The YAML’s named rule selection is not a complete rule engine. |
| [jsnkle/ai-native-sdlc](https://github.com/jsnkle/ai-native-sdlc) | 1; push not found. [Changelog](https://github.com/jsnkle/ai-native-sdlc/blob/main/CHANGELOG.md): v0.2.7, 2026-09-26. | [`ops/detect.py`](https://raw.githubusercontent.com/jsnkle/ai-native-sdlc/main/plugin/template/ops/detect.py) consumes GitHub Actions results or fixtures, computes rolling failure signals and emits tiers. | MIT; detector runs locally. Its surrounding agent loop can incur model costs. | Actions-specific series and overlapping failure windows; not a general JSONL/CSV policy CLI. Establishes prior art for tiers and operational escalation. |
| [shewhart](https://github.com/bertanucar/shewhart), Python | 3; push not found. [PyPI](https://pypi.org/project/shewhart/): 0.1.1, 2026-06-12. | Advertises Western Electric 1-4, Nelson 1-8, structured review results and frozen JSON baselines. | MIT; free library. Published wheel is 52.4 kB, excluding dependencies. | Statistical engine is substantially occupied; policy files, incident lifecycle and delivery remain integration work. |
| [waylen888/alarm](https://github.com/waylen888/alarm), Go | 0; push not found. [Documented v0.3.2](https://pkg.go.dev/github.com/waylen888/alarm@v0.3.2/spc): 2026-08-27; not asserted to be latest. | Nelson rules, EWMA/CUSUM, fixed/trailing/robust baselines and multi-level firing/resolution state. | MIT; repository describes no external dependencies. | Strong overlap beyond arithmetic. A CLI would mostly add input conventions, configuration validation and destinations. |
| [Forward Impact libxmr / Gemba](https://github.com/forwardimpact/monorepo), JavaScript | 6; push not found. [Library README](https://raw.githubusercontent.com/forwardimpact/monorepo/main/libraries/libxmr/README.md) includes a dated 2026-08-26 decision. | `gemba-xmr` CLI and library classify metric series; explicit insufficient-data and degenerate cases, signal provenance and recomputation handling. | Apache-2.0; local tooling. | Already targets coding-agent measurement. Uses XmR/Wheeler-Vacanti rules rather than a general Western Electric/Nelson policy-and-delivery contract. |
| [Anomalyzer](https://github.com/PredictabilityAtScale/anomaly-detection) | 2; push and dated activity not found. | Python CLI/MCP detector with CSV/JSON, policy/evidence concepts and statistical detectors. | MIT; local use. | Significant general detector overlap. Documentation explicitly leaves scheduling, notification and operational actions to the caller. |
| [github-action-benchmark](https://github.com/benchmark-action/github-action-benchmark) | 1.3k; push not found. [Changelog](https://github.com/benchmark-action/github-action-benchmark/blob/master/CHANGELOG.md): v1.22.1, 2026-05-06. | Threshold regressions can create PR comments, fail jobs and produce GitHub notifications. | MIT; Actions usage subject to normal account allowances. | Delivery is established prior art. Comparing a benchmark with a previous value is not the requested rolling statistical detector. |

The existing [bands.yaml](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/skills/ai-native-sdlc/assets/bands.yaml) already names a rolling baseline, Western Electric rules, tiers and routes. A viable successor needs precise semantics rather than merely adopting those keys.

A proposed contract would specify:

- **Observations:** schema version, timestamp, metric, value, unit, cohort dimensions, unique observation ID; numerator and denominator for rates.
- **Baseline:** fixed versus trailing; count/time window; minimum observations; estimator; exclude the tested observation; freeze/reset policy; handling of missing, late, duplicate and zero-variance data.
- **Rules:** named/versioned family, enabled rules, sidedness, equality conventions, run lengths and metric direction. Distinguish Gaussian measurements from binary outcomes and variable-denominator rates.
- **Verdicts:** rule evidence, baseline identity, supporting observation IDs, tier mapping and explicit `insufficient_data`; avoid treating every Nelson pattern as a “three sigma event.”
- **Incidents and output:** stable episode ID, escalation/recovery, cooldown, state persistence, JSON/Markdown rendering, destination, dry run and retry behavior. GitHub issue updates need deduplication across crashes.

These are proposed requirements inferred from the inspected implementations. No source establishes one canonical `bands.yaml` standard.

## E. Users beyond the lab

| Tool or project | Stars, last push | What it does | Openness and cost | Gap for this family |
|---|---|---|---|---|
| [openai/codex-action](https://github.com/openai/codex-action) users | 1.3k; push and dated activity not found. | Runs Codex in GitHub Actions, providing a natural place to capture run/session/commit receipts. | Apache-2.0 action; model and runner costs remain separate. | CI operators could compare prompt/model changes against later checks and review outcomes. Logs must be retained before runners disappear. |
| [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) users | 9.5k; push and dated activity not found. | Claude-driven repository tasks and reviews through GitHub workflows. | MIT action; model and runner costs remain separate. | Similar audience, with explicit workflow identity making attribution easier than historical laptop logs. |
| [Scott Logic AnthropicSDLCExample](https://github.com/amjones-scottlogic/AnthropicSDLCExample) | 0; push and dated activity not found; license not found. | [`capture.mjs`](https://raw.githubusercontent.com/amjones-scottlogic/AnthropicSDLCExample/main/.claude/skills/capture-metrics/capture.mjs) joins Claude transcript usage by branch to PR metrics and updates a PR comment. Review rounds use changes-requested reviews followed by commits. | Public, dependency-free JavaScript source; reuse rights require checking. | Closest concrete overlap for niche 2. Codex support, exact commit attribution and autonomous-resolution proof are not established. |
| `bashebr` and `jsnkle` template authors/users | 80 and 1 respectively; push not found; activity above. | Their existing detector/configuration workflows are plausible integration points. | MIT templates; deterministic detection can remain free. | They may prefer a small upstream improvement over another product. Repository popularity does not demonstrate demand or willingness to maintain adapters. |
| Solo developers using the above CLIs | N/A; audience hypothesis. | Could retain local evidence and inspect regressions without a hosted dashboard. | Proposed offline analysis has no service cost. | Low PR volume, changing projects and heterogeneous tasks may make statistical bands uninformative. Immediate per-PR evidence may be more useful than trend alerts. |

The strongest audience evidence is executable integration code, especially Scott Logic’s collector and the two template detectors. Stars establish visibility, not active usage. This sweep did not establish paying demand or a sufficiently large homogeneous telemetry stream among solo developers.

## Research or practitioner baselines

- **Control-chart false alarms:** NIST gives approximately **one false alarm per 371 observations** for a two-sided three-sigma rule under its stated assumptions. Applying additional run rules changes that rate; correlated CI outcomes do not automatically satisfy the assumptions. [NIST control-chart guidance](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm).
- **Rolling baselines can absorb regressions:** the Go `alarm` documentation discusses a sustained shift eventually entering the trailing baseline and allowing resolution while the process remains shifted. Baseline freezing/reset policy is therefore product behavior, not a cosmetic option. [Go SPC documentation](https://pkg.go.dev/github.com/waylen888/alarm@v0.3.2/spc).
- **Minimum-data behavior already has precedent:** libxmr requires at least **15 points** and distinguishes insufficient data and degenerate limits. That is its implementation policy, not evidence that 15 heterogeneous PRs yield a trustworthy SDLC alarm. [libxmr README](https://raw.githubusercontent.com/forwardimpact/monorepo/main/libraries/libxmr/README.md).
- **Productivity inference remains difficult:** METR’s February 2026 update reports **57 developers, 143 repositories and 800+ tasks**, but calls the updated productivity signal unreliable because of selection and measurement effects. Its earlier 19% slowdown should not be presented as a current coding-agent effect. Session-to-PR joins support observation, not causal productivity claims. [METR update](https://metr.org/blog/2026-02-24-uplift-update/).
- **“Plan followed” is not cheaply solved:** Scott Logic’s implementation leaves the verdict unknown until a plan-review judgment is recorded. This is useful precedent for preserving unknowns rather than inferring semantic compliance from file overlap. [Collector source](https://raw.githubusercontent.com/amjones-scottlogic/AnthropicSDLCExample/main/.claude/skills/capture-metrics/capture.mjs).

## Unoccupied niches

1. **Niche 2, narrowed: portable cross-agent attribution with evidence and coverage reporting.**  
   Scott Logic already joins Claude usage to PR metrics; native analytics and Opaline cover adjacent territory. No inspected source established exact cross-agent commit receipts plus first-attempt CI, review history and explicit uncertainty in one small local CLI.

2. **Niche 4, narrowed: a rigorously specified detector with reliable issue delivery.**  
   Detectors, bands configuration, tiers and notifications each exist. No inspected implementation established the complete combination of JSONL/CSV, precise configurable rules, replayable baselines, persisted incident lifecycle and deduplicated GitHub issue delivery.

3. **Evidence of human intervention, rather than guessed autonomy.**  
   GitHub resolution state cannot establish who performed the fix; Pinrail records explicit human decisions but does not know the repository. A receipt linking intervention, revision and outcome remains a possible integration gap, not a verified empty market.

## Candidate products

### 1. `pr-evidence`: session-to-PR evidence ledger

**Pitch:** A local CLI that links Codex and Claude sessions to GitHub outcomes, showing the evidence and reporting ambiguous joins.

**Twelve-day scope, six two-day increments; commands below are proposed acceptance checks:**

1. Versioned normalized event format and streaming importers for supplied Codex/Claude fixtures. Ship `uv run pr-evidence import fixtures/ --out evidence.db`; `uv run --with pytest pytest -q tests/test_import.py` verifies forks, missing fields and malformed records.
2. Git/session receipts and deterministic joins, with branch/time suggestions kept separate. Ship `uv run pr-evidence link --receipts fixtures/receipts.jsonl`; `pytest` fixtures cover worktrees, branch reuse, squash and rebase.
3. GitHub snapshot importer with pagination and incremental caching. Ship `uv run pr-evidence github --fixture fixtures/github/`; fake HTTP responses verify pagination, retry and missing permissions.
4. Explicit first-attempt CI and review-round calculations. Ship `uv run pr-evidence outcomes --db evidence.db`; golden fixtures verify failed-then-passing attempts, synthetic merge SHAs and incomplete history.
5. Markdown/JSON reports with attribution coverage and unknown reasons. Ship `uv run pr-evidence report --format markdown`; snapshot checks ensure unsupported autonomy and plan claims remain unknown.
6. CI artifact example, receipt-based plan/check references and installation smoke test. Ship `uv run pr-evidence self-check`; an end-to-end fixture command reproduces the same report twice.

**Footprint:** Python with `uv`, stdlib SQLite/JSON/CSV and existing `git`/`gh`; no server or model dependency. Proposed budget: package/environment below 50 MB excluding installed Python/uv/gh, capped cache 100 MB, streaming import below 150 MB RSS. Measure during the spike; no Docker or downloaded dataset.

**Users:** Small teams running agents in CI; maintainers comparing agent configurations; solo developers needing per-PR audit evidence. Existing-log analysis is free; creating new agent runs is outside that cost claim.

**Strongest argument against it:** Branch-level collectors already provide much of the visible benefit. Reliable attribution requires new instrumentation, and existing sessions may remain mostly unjoinable.

**Riskiest assumption and one-day spike:** Enough sessions can be linked through explicit receipts without brittle transcript interpretation. Use a disposable repository and permitted test sessions/fixtures covering both agents, resume, model change, worktrees, shared branches, squash and rebase. Compare against a manually specified commit ledger. Require zero falsely asserted exact joins; publish coverage separately. If receipts cannot reliably capture output revisions, reduce scope before building reports.

### 2. `bands-run`: deterministic telemetry verdicts with incident delivery

**Pitch:** Feed JSONL or CSV and `bands.yaml`; receive a replayable verdict and an optional deduplicated GitHub issue, without an LLM.

**Twelve-day scope, six two-day increments; commands below are proposed acceptance checks:**

1. Strict observation/config validation and JSONL/CSV normalization. Ship `uv run bands validate --config examples/bands.yaml --input examples/metrics.csv`; fixtures verify invalid units, duplicate IDs and ordering policy.
2. Frozen/trailing baselines and explicitly selected Western Electric/Nelson rules. Ship `uv run bands replay examples/signals.jsonl`; independent hand-calculated vectors verify each supported rule and boundary.
3. Tiers, warm-up, zero variance and baseline provenance. Ship `uv run bands explain --event example-17`; tests verify the exact observations and baseline behind each verdict.
4. Persisted incident episodes, escalation, recovery and replay idempotency. Ship `uv run bands replay examples/incident.jsonl --state incidents.db`; running twice must produce no duplicate transitions.
5. GitHub issue renderer and opt-in publisher, with local message output. Ship `uv run bands publish --dry-run`; fake API tests cover timeout-after-create, duplicate prevention and retries.
6. One SDLC input adapter, packaging and resource checks. Ship `uv run bands self-check` and a deterministic synthetic-stream benchmark; document supported metric distributions and measured limits.

**Footprint:** Python with `uv`, PyYAML and stdlib statistics/SQLite; no pandas, plotting stack, service or model call. Proposed budget: environment below 30 MB excluding Python/uv, state capped at 50 MB, below 100 MB RSS for bounded windows. Entire offline path is free; GitHub publishing uses the user’s existing account.

**Users:** Template maintainers, small CI fleets and teams already exporting consistent numeric telemetry. Start with stable continuous metrics; binary CI outcomes need an explicit rate model rather than treating zeros and ones as Gaussian measurements.

**Strongest argument against it:** This may be a thin integration layer over existing libraries and templates. Sparse, correlated SDLC data could make its notifications less useful than simple explicit thresholds.

**Riskiest assumption and one-day spike:** Selected rules can produce useful incident behavior without excessive false alerts or absorbing persistent regressions. Generate seeded independent noise, autocorrelated noise, step shifts and variable-denominator failures; replay fixed and rolling baselines against independent reference calculations. Measure alert frequency, detection delay and recovery behavior. Failure to explain these results would block broad statistical claims, even if the CLI works.

## Sources

- Local brief inputs: `intent/README.md`; `intent/research/landscape-2026-10-15.md`; repository `AGENTS.md`.
- Codex: [repository](https://github.com/openai/codex), [releases](https://github.com/openai/codex/releases), [rollout protocol](https://raw.githubusercontent.com/openai/codex/main/codex-rs/protocol/src/protocol.rs), [recorder](https://github.com/openai/codex/blob/main/codex-rs/rollout/src/recorder.rs).
- Codex published interfaces: [Thread schema](https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript/v2/Thread.ts), [GitInfo schema](https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript/v2/GitInfo.ts), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).
- Claude Code: [repository](https://github.com/anthropics/claude-code), [releases](https://github.com/anthropics/claude-code/releases), [hooks](https://code.claude.com/docs/en/hooks), [analytics](https://code.claude.com/docs/en/analytics).
- Claude session reading: [SDK repository](https://github.com/anthropics/claude-agent-sdk-python), [official cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-05-building-a-session-browser), [types](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/types.py), [reader implementation](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/_internal/sessions.py).
- GitHub REST: [check runs](https://docs.github.com/en/rest/checks/runs), [workflow runs](https://docs.github.com/en/rest/actions/workflow-runs), [pull requests](https://docs.github.com/en/rest/pulls/pulls), [commits](https://docs.github.com/en/rest/commits/commits).
- GitHub GraphQL: [pull-request types](https://docs.github.com/en/graphql/reference/pulls), [commit types](https://docs.github.com/en/graphql/reference/commits).
- GitHub constraints: [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [GraphQL rate limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api), [Copilot attribution/security](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/risks-and-mitigations).
- Freshness: [Mixpanel announcement](https://mixpanel.com/blog/mixpanel-agent-intelligence/), [Pinrail repository](https://github.com/forgeplane/pinrail), [Pinrail Show HN](https://news.ycombinator.com/item?id=49995778), [Opaline CLI](https://github.com/opalinehq/cli), [Opaline Product Hunt launch](https://www.producthunt.com/products/rudel?launch=opaline).
- Bashebr: [repository](https://github.com/bashebr/ai-native-sdlc), [detector](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/skills/ai-native-sdlc/scripts/detect_bands.py), [bands configuration](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/skills/ai-native-sdlc/assets/bands.yaml), [changelog](https://raw.githubusercontent.com/bashebr/ai-native-sdlc/main/CHANGELOG.md).
- Jsnkle: [repository](https://github.com/jsnkle/ai-native-sdlc), [detector](https://raw.githubusercontent.com/jsnkle/ai-native-sdlc/main/plugin/template/ops/detect.py), [changelog](https://github.com/jsnkle/ai-native-sdlc/blob/main/CHANGELOG.md).
- Python SPC: [shewhart repository](https://github.com/bertanucar/shewhart), [PyPI release](https://pypi.org/project/shewhart/), [Anomalyzer](https://github.com/PredictabilityAtScale/anomaly-detection).
- Go SPC: [alarm repository](https://github.com/waylen888/alarm), [v0.3.2 documentation](https://pkg.go.dev/github.com/waylen888/alarm@v0.3.2/spc).
- JavaScript SPC: [Forward Impact repository](https://github.com/forwardimpact/monorepo), [libxmr README](https://raw.githubusercontent.com/forwardimpact/monorepo/main/libraries/libxmr/README.md).
- Notification prior art: [benchmark action](https://github.com/benchmark-action/github-action-benchmark), [changelog](https://github.com/benchmark-action/github-action-benchmark/blob/master/CHANGELOG.md).
- CI audiences: [Codex action](https://github.com/openai/codex-action), [Claude Code action](https://github.com/anthropics/claude-code-action).
- Existing session/PR collector: [Scott Logic example](https://github.com/amjones-scottlogic/AnthropicSDLCExample), [capture implementation](https://raw.githubusercontent.com/amjones-scottlogic/AnthropicSDLCExample/main/.claude/skills/capture-metrics/capture.mjs).
- Baselines: [NIST control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm), [METR February 2026 update](https://metr.org/blog/2026-02-24-uplift-update/).