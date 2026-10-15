# Landscape sweep, 2026-10-15 (supervisor's research agent, before phase 1)

Method: web search, page fetches and `gh api` for stars and last-push dates on 2026-10-15. This
is input to phase 1, not a decision. Star counts are point in time.

## A. SDLC and DORA-style metrics for agent-written code

| Tool | Measures | Source | Openness | Gap |
| --- | --- | --- | --- | --- |
| Swarmia AI measurement | per-tool throughput, cycle time, batch size, review time; agent PRs merged vs closed; detection by co-author trailers and labels | GitHub metadata | commercial | no first-pass CI, no rework per PR, no comments-resolved-without-human |
| DX AI Measurement Framework | utilisation, impact, cost; AI-assisted PR share; local daemon for line attribution | daemon, git, surveys | enterprise | surveys heavy; no CI first-pass |
| Faros AI | AI impact alongside DORA; rework on AI code | tool APIs, git, CI | enterprise | detection method undocumented |
| Zest | which agent sessions led to which PRs; agentic loop stage medians | GitHub App | free 3 seats, then paid, closed | no DORA, no first-pass, no rework |
| GitKraken Insights | DORA plus "AI rework, duplication, defects" | git, CI | paid | marketing-level detail |
| coderbuds/ai-detector (4 stars, MIT) | YAML rules detecting Claude, Copilot, Cursor, Codex PRs | GitHub | rules open, product closed | rules only |
| git-ai-project/git-ai (2.8k stars, now part of OpenAI) | line-level AI authorship; per-PR ai_aided, percent_ai, model, cost | git extension plus hosted API | CLI open, analytics hosted | attribution, not outcomes |
| GitHub Copilot usage metrics API | agent PRs created and merged, median time to merge | GitHub native | with Copilot Business | Copilot only |
| Claude Code analytics (Teams, Enterprise) | PRs and lines with Claude Code; labels PRs | Claude GitHub app plus sessions | plan feature | attribution and volume only |
| Apache DevLake (3.2k), Four Keys (archived) | generic DORA | git, CI | open | no agent attribution |
| LangWatch (5k, open core) | session to PR join; cost per PR and model | sessions plus GitHub | open core | cost only |

Research baselines: arXiv 2602.08915 (Copilot 4.94 reviews per PR vs Codex 1.39; acceptance 68.0
vs 77.9 percent), 2609.26847 (post-merge follow-up fix rates 3 to 5 percent by agent), 2606.24429
(commit-based census misses essentially all Codex adopters). Attribution undercounting is
systemic; any metric must report the unattributed share.

Gap: no product computes first-pass CI success for agent PRs or the share of review comments
resolved without a human, by agent. Everyone has attribution, cycle time or cost.

## B. Local session log analysis and OpenTelemetry

Claude Code native OTel: 8 metrics (session count, lines of code, PR count, commit count, cost,
tokens, edit decisions, active time) and events (user_prompt, tool_result, tool_decision,
api_request, api_error, permission_mode_changed, skill_activated). Not exported: PR or CI
outcomes beyond counts.

| Project | Stars | What | Gap |
| --- | --- | --- | --- |
| ccusage/ccusage | 19k | token and cost CLI over Claude Code JSONL | cost only |
| jhlee0409/claude-code-history-viewer | 2.3k | desktop viewer, 31 agents, cost, skills, export | browse plus cost |
| d-kimuson/claude-code-viewer | 1.3k | web client, search | stalling |
| chiphuyen/sniffly | 1.3k | usage and error dashboard | dead 14 months |
| daaain/claude-code-log | 1.2k | JSONL to HTML/Markdown | rendering |
| vshulcz/deja-vu | 1.2k | unified search across 40 agents | memory, not metrics |
| ctxrs/ctx | 1.2k | "git blame for agent sessions" | recall |
| jazzyalex/agent-sessions | 0.9k | macOS app, several agents | browse |
| es617/claude-replay | 0.8k | session replay, several agents | replay |
| entireio/cli | 5.2k, MIT | sessions as checkpoints in git refs, commit trailers, activity and token reports | links sessions to commits, not PRs; no SDLC metrics |
| flight recorder cluster (flightrec, agentmetry, agent-session-recorder, agentlens, openvcr, midflight-replay) | 0 to 14 | record and replay, audit timelines | zero traction |
| OTel dashboards (claude-code-metrics-prometheus 17, claude-code-metrics-stack 11, Grafana 25255 and others) | low | Prometheus and Grafana over the 8 native metrics | stop at cost and tokens |
| Codex: codex-session-viewer, codex-transcripts (17), codex-transcript-viewer (24), codex-sessions | low | rollout viewers | Codex only |

Gap: every tool is a viewer, a cost aggregator or a memory index. None joins local sessions to
PR outcomes (first-pass CI, review rounds, plan followed). Only Scott Logic's `capture.mjs`
(0 stars) does the join, and posts to PR comments.

## C. Spec-driven frameworks and drift

| Project | Stars | Drift or metrics |
| --- | --- | --- |
| github/spec-kit | 141k | reconcile extension in review; no metric |
| Fission-AI/OpenSpec | 72k | sync and structural validate; no drift score |
| bmad-code-org/BMAD-METHOD | 54k | manual QA agent review |
| buildermethods/agent-os | 5.5k | standards injection |
| Kiro (AWS) | commercial | requirements, design, tasks; traceability stated, no report |
| fiberplane/drift | 151 | AST-fingerprint stale-doc flag in CI; quiet since June |
| nandeshkanagaraju/specdrift-bench | 0 | drift check CLI, brand new |
| ai-sdlc-framework/ai-sdlc | 411 | metrics spec (task success, intervention rate, churn, cost) fed only by its own orchestrator |

Gap: the big three compute nothing from their artifacts; drift tooling is binary, not a series.

## D. Deterministic control bands on engineering telemetry

| Project | Stars | What | Gap |
| --- | --- | --- | --- |
| jsnkle/ai-native-sdlc detect.py | 1 | bands.yaml, gh run list, z-score tiers, tests | one metric, Actions only |
| bashebr/ai-native-sdlc bands.yaml | 80 | playbook-shaped config | config only, no detector |
| grafana/promql-anomaly-detection | 424 | adaptive bands in Prometheus | needs Prometheus |
| PredictabilityAtScale/anomaly-detection (Anomalyzer) | 2, alpha | CSV/JSON, Nelson rules, CUSUM | no alerting |
| shewhart (PyPI) | new | Nelson 1 to 8 and WE 1 to 4 as events, NIST validated | library only |
| pyspc, nelsonRules, WE_Rules, R weco | dead | batch rule evaluators | not CLIs |
| healthchecks.io, Cronitor | active | dead-man switch for cron | no duration or outcome bands |

Gap: no small open CLI takes JSONL/CSV plus a bands.yaml (rolling baseline, Western Electric,
tiers) and emits a tiered verdict plus an issue or message.

## E. Implementations of the playbook

No official template or dashboard. Vendors (Waydev, Port, Atlassian) wrote "the playbook lacks
measurement" posts. Repos: amjones-scottlogic/AnthropicSDLCExample (0 stars; the only code that
computes indicators: a hook posting a metrics table comment per PR from git, GitHub and local
transcripts; Deploy metrics "not yet defined"); jsnkle/ai-native-sdlc (1; documents the table,
computes none); bashebr/ai-native-sdlc (80; templates and skill, no metrics); several zero-star
starters.

## Unoccupied niches, as the agent saw them

1. Agent-attributed Test and Deploy leading indicators from GitHub alone.
2. Local-session to PR-outcome join (Claude Code and Codex JSONL to PR CI and review outcome).
3. Artifact-derived metrics for spec-driven frameworks (intent to spec hours, spec commits after
   plan, plan-to-merge, plan-match), from git log on the artifact paths.
4. A bands.yaml-driven deterministic detector CLI with issue or message output.
5. Cross-agent comparison on the same kind of task inside one team, handling the Codex
   attribution asymmetry (no commit trailers).

Sources are in the agent's transcript; the main ones: Anthropic playbook, Claude Code monitoring
and analytics docs, Swarmia, DX, Faros, Zest, Coderbuds, Git AI, GitHub changelog, LangWatch,
Entire, the repos named above, arXiv 2602.08915, 2609.26847, 2606.24429.
