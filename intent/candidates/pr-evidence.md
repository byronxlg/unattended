# Candidate intent: pr-evidence
Drafted 2026-10-16 by Codex job candidate-pr-evidence-d1; a draft for the supervisor, not a decision.

## Problem

The lab needs to connect agent work to CI, review and merge outcomes. `docs/metrics.md` asks for first-pass CI on agent-written changes, review timing and comments resolved without human branch edits. Today the supervisor has job receipts, GitHub records and manually recorded change outcomes, but no durable evidence connecting them.

The sweep's nearest executable precedent is Scott Logic's [capture.mjs](https://raw.githubusercontent.com/amjones-scottlogic/AnthropicSDLCExample/main/.claude/skills/capture-metrics/capture.mjs). Its inspected source aggregates Claude usage by branch and counts changes-requested reviews followed by commits. That demonstrates an existing use case, but branch association alone cannot distinguish reused branches, overlapping sessions or rewritten commits. The sweep identified portable attribution with explicit uncertainty as the narrower opportunity, not another token dashboard.

### What this lab already records

Inspection of `bin/codex-run`, the ledger and two completed event streams showed:

| Evidence | Present | Missing or insufficient |
| --- | --- | --- |
| Ledger identity | `id`, `kind`, `change`, `thread_id` | Schema version, agent CLI version, canonical repository identity, explicit resume relationship |
| Execution context | `cwd` relative to repository root, `sandbox`, `started`, `ended`, `duration_s`, `rc`, `killed` | Captured branch, stable worktree identity, before/after HEAD, output commit list, dirty-state boundaries |
| Accounting | `model`, `usage`, `rate_limits`, `items`, `diff`, `last_message` | Per-turn model history; `diff` is a shortstat, not commit evidence |
| Events | `thread.started.thread_id`, turn events and `turn.completed.usage`; item events | No structured repository, branch or HEAD receipt in the inspected streams |
| Command items | `command`, `aggregated_output`, `exit_code`, `id`, `status`, `type` | Arbitrary command text is not a guaranteed commit capture protocol |

The wrapper computes `BASE_SHA` before execution, passes it to its accounting code and uses it for `git diff --shortstat`. It does **not** persist it. It never captures ending HEAD or branch. The relative `cwd` identifies a location, but cannot recover a removed worktree's history.

The wrapper source also reads private Codex rollouts for model/rate information. This research did not execute the wrapper or inspect those files. New attribution must work from explicit repository-local receipts.

Exact ledger line, obtained with `sed -n '1p' state/ledger.jsonl`:

```json
{"id": "smoke-0", "kind": "research", "change": null, "started": "2026-10-15T08:26:59Z", "ended": "2026-10-15T08:27:09Z", "duration_s": 10, "rc": 0, "killed": false, "sandbox": "read-only", "cwd": ".", "model": "gpt-6-astra", "thread_id": "01a13eab-f90f-72e1-aefa-8a585048f968", "usage": {"input_tokens": 19615, "cached_input_tokens": 12928, "cache_write_input_tokens": 0, "output_tokens": 5, "reasoning_output_tokens": 0}, "rate_limits": null, "items": {"agent_message": 1}, "diff": null, "last_message": "ok"}
```

This is sufficient for job accounting, not an exact session-to-commit join. At inspection, all six completed ledger entries were research jobs; no completed build receipt was available to validate.

## Proposed outcome

By build day 12, a local Python library and CLI explain which supplied Codex or Claude session runs contributed commits to a PR, which evidence supports each link, and which outcomes remain unknown. No model calls are required.

Proposed command contract, not commands implemented or verified today:

| Command | What it prints |
| --- | --- |
| `uv run --project product pr-evidence import --ledger state/ledger.jsonl --receipts receipts.jsonl --db evidence.db` | Imported, duplicate, rejected and unsupported record counts, with reasons |
| `uv run --project product pr-evidence github --repo byronxlg/unattended --db evidence.db` | Snapshot IDs, collection time, pagination completeness and permission/history gaps |
| `uv run --project product pr-evidence explain --repo byronxlg/unattended --pr "$pr_number" --db evidence.db` | Session-run → receipt → original commit → PR → merge evidence; ambiguous alternatives separately |
| `uv run --project product pr-evidence report --db evidence.db --format json` | Versioned outcomes, coverage numerators/denominators, unknown reasons and source references |
| `uv run --project product pr-evidence self-check` | `self-check: PASS` only after its offline acceptance assertions pass |

### Join contract and squash survival

`prompts/supervisor.md` creates `.worktrees/<change>` on `change/<slug>`, dispatches a build there, then opens a PR and squash-merges it. Use that branch and worktree to find candidate PRs, then verify repository identity and original commit membership. Branch name and time alone produce a suggested link, never an exact one.

Each invocation needs a versioned receipt containing job/session IDs, agent/version, repository identity, worktree identity, branch before/after, timestamps, before/after HEAD, dirty-state boundaries and the explicit output commit list. Resumed jobs retain their own invocation IDs even when they share a session ID. Record interrupted or incomplete receipts rather than silently dropping them.

An exact job attribution requires an exclusively assigned worktree, a clean starting boundary, an ancestor relationship between captured HEADs and no unexplained intervening writer. A commit range alone does not prove authorship. Shared worktrees, dirty input, imported commits and unrecorded rewrites lower confidence.

**Before squash or worktree removal**, retain the job receipts, original commit SHAs, PR repository/number/node ID, head repository/ref/SHA, base SHA and paginated PR commit snapshot. Preserve earlier head snapshots when revisions change. After merge, append the merge SHA and timestamp to the same PR identity. The squash commit is a new identity; walking `main` cannot recover the original session boundaries. Rebase/amend mappings require explicit transition evidence or remain unknown. GitHub documents PR head/base and merge fields in its [PR REST reference](https://docs.github.com/en/rest/pulls/pulls).

### Operational outcome definitions

GitHub documents formal `reviews`, ordinary PR `comments`, and `reviewThreads` with `isResolved`, `isOutdated` and nullable `resolvedBy`. These can be queried through GraphQL, but neither “review rounds” nor “fixed without a human” is a native measured fact. Ordinary discussion comments do not have review-thread resolution state. [GraphQL pull-request reference](https://docs.github.com/en/graphql/reference/pulls).

Proposed lab definitions from day one:

- **Review round:** one distinct reviewed PR head SHA with a completed, identified review. Supervisor and Codex assessments of the same SHA count as two assessments in one round. A reviewed revision creates another round. Report additional rounds separately as `max(rounds - 1, 0)`.
- **Agent review identity:** every review summary carries a versioned marker containing reviewer role, job/session reference, reviewed SHA and verdict. The supervisor may post the read-only Codex job's result with that job reference. A shared GitHub login does not identify which agent acted. Unmarked historical comments remain unclassified.
- **Review timing:** first review is the earliest qualifying submitted review or marked review comment after PR creation. Supervisor review time ends at its first completed assessment. Preserve native submission time versus comment-posting time as different sources.
- **Resolution unit:** one actionable finding, identified by a root thread/comment ID or a stable finding ID inside a marked summary. Replies do not enlarge the denominator. Ordinary comments need an explicit resolution record linking finding, fix job, revision and supervisor acceptance; native threads retain their native resolution evidence too.
- **Without human branch edits:** classify a resolved finding as `agent_only_attested` only with continuous branch receipts through resolution and an explicit no-human-edit attestation. Known human edits produce `human_involved`; gaps or shared credentials without receipts produce `unknown`. Resolver identity alone is insufficient. Report counts and the conservative attested share of all resolved findings per PR, including unknowns in that denominator; zero resolved findings means no data.
- **First-attempt CI:** for each captured PR head, select `.github/workflows/ci.yml` on `pull_request`, its earliest matching run and attempt 1. All configured jobs must succeed. Failure remains failure after reruns; missing, pending, cancelled or skipped required work remains separately classified. Retain PR head and tested merge SHA separately. Attempt-specific retrieval is documented in [workflow runs](https://docs.github.com/en/rest/actions/workflow-runs).
- **Aggregation:** retain the existing per-head metric from `docs/metrics.md`; additionally expose an explicitly named initial-head PR metric. Never substitute latest green checks for either. Merge outcome records merged/open/closed state independently of deployment.

The sentence “here all comments are agent-resolved” in `docs/metrics.md` is a lab assumption, not evidence. Its replacement and these definitions need supervisor acceptance.

### Coverage and boundary with bin/metrics

Report three denominators: eligible build/fix invocations, eligible PRs in the selected repository/time window, and original commits in complete PR snapshots. Show exact, suggested, ambiguous and unknown attribution separately. Exclude known research/review-only invocations explicitly; do not discard failed or unjoinable build jobs. Missing PR history makes commit coverage unknown.

`pr-evidence` owns portable receipts, adapters, GitHub snapshots, joins, outcome definitions and evidence reports. `bin/metrics` consumes its versioned JSON/library API for Test/Deploy data, then combines lab-specific intent history, changes, incidents, costs and deployment indicators and renders the blog. It must not implement a second join or review-round calculator. `bin/metrics` was not present in the inspected file inventory; this boundary is a proposal against its intent.

Out of scope: hosted dashboards, automatic PR comments, model ranking, causal productivity claims, line-level authorship, automatic “plan followed” judgments, universal historical transcript parsing, statistical alerts and the rest of the lab's metrics.

## Affected users and systems

User one is the supervisor maintaining this lab's metrics and blog. Secondary users are maintainers running Codex or Claude in isolated worktrees or CI. Systems affected are the product package, receipt instrumentation in `bin/codex-run`, supervisor review conventions, `bin/metrics`, repository-local evidence storage and GitHub read APIs.

Claude support starts with explicitly supplied hook receipts, using documented `session_id` and `cwd`; private transcript crawling is unnecessary. [Claude hook reference](https://code.claude.com/docs/en/hooks).

## Constraints

- Python with `uv`; stdlib JSON, SQLite, subprocess and hashing first. A small Go or JS implementation remains acceptable if the supervisor changes the language choice.
- Free analysis of existing evidence; no model subscription, hosted service, Docker or downloaded dataset required. Existing agent execution and GitHub account limits remain separate.
- Stay within the host's under-2-GiB available disk. Proposed budgets: package/environment under 50 MiB excluding existing tools, bounded cache at 100 MiB; measure rather than assume.
- Every increment has an offline CI command. Use tiny synthetic fixtures, deterministic ordering and explicit schema versions; retain malformed-record diagnostics and duplicate detection.
- GitHub access is read-only. Request only required read permissions, paginate every connection, cache immutable evidence and expose rate/permission failures.
- Store minimal structured evidence. Do not publish prompts, transcript bodies, secrets or absolute home paths; preserve evidence hashes and relevant source IDs.
- This research changes no files. Integration edits listed below belong to later authorized build jobs.

## Increments

All commands and expected results below are proposed acceptance criteria, not observed outputs.

| Build days | Files and shipped behavior | Proving command and expected result | Blog evidence |
| --- | --- | --- | --- |
| 1-2 | `product/pyproject.toml`, `product/pr_evidence/schema.py`, `importers.py`, `tests/test_import.py`, small `tests/fixtures/`; normalize lab/Codex events and Claude hook receipts | `uv run --project product --with pytest pytest -q product/tests/test_import.py`; exit 0, assertions cover missing fields, malformed input, resume and duplicate imports | The actual smoke receipt beside its normalized record and missing fields |
| 3-4 | `product/pr_evidence/receipts.py`, `joins.py`, `tests/test_joins.py`, `bin/codex-run`; capture boundaries and explain joins | `uv run --project product --with pytest pytest -q product/tests/test_joins.py`; exit 0, exact isolated join survives squash; reused/shared branches never become exact | One before/after receipt and an intentionally ambiguous example |
| 5-6 | `product/pr_evidence/github.py`, `tests/test_github.py`, paginated response fixtures; snapshot PRs, reviews and Actions | `uv run --project product --with pytest pytest -q product/tests/test_github.py`; exit 0, later pages retained and interrupted/403 histories marked incomplete | A source-linked PR snapshot, or the precise live-access limitation |
| 7-8 | `product/pr_evidence/outcomes.py`, `tests/test_outcomes.py`, `docs/metrics.md`, `prompts/supervisor.md`; adopt explicit review markers and metric definitions | `uv run --project product --with pytest pytest -q product/tests/test_outcomes.py`; exit 0, fail-then-pass stays first-attempt failure; two agents on one SHA count one round; unproven autonomy stays unknown | Why green CI and resolved comments can mislead |
| 9-10 | `product/pr_evidence/report.py`, `tests/test_report.py`, `bin/metrics` integration; JSON/Markdown explanations and coverage | `uv run --project product --with pytest pytest -q product/tests/test_report.py`; exit 0, denominators include unjoined work and empty cohorts report no data | The lab's measured coverage, including holes |
| 11-12 | `product/pr_evidence/self_check.py`, `product/README.md`, `tests/test_integration.py`, `.github/workflows/ci.yml` and `pages.yml`; CI and thin metrics caller | `uv run --project product pr-evidence self-check`; expected `self-check: PASS`; `uv run --with pytest pytest -q` and `bin/lint` must also exit 0 | Replay the same snapshot twice, compare identical reports, publish measured footprint and remaining gaps |

The CI edit must ensure product tests actually execute. The inspected workflow guards pytest with an `ls` over both root and product test globs; the integration check must verify collection rather than accept “no tests yet”.

## Spike

**Riskiest assumption:** a small receipt addition can establish useful exact joins under the lab's worktree/squash workflow without claiming that every commit inside a session interval belongs to that agent.

Read-only checks run during this research:

```sh
jq -r -s '"completed_jobs=\(length) build_or_fix_jobs=\(map(select(.kind=="build" or .kind=="fix"))|length) missing_branch=\(map(select(has("branch")|not))|length) missing_head_before=\(map(select(has("head_before")|not))|length) missing_head_after=\(map(select(has("head_after")|not))|length)"' state/ledger.jsonl
```

Observed output:

```text
completed_jobs=6 build_or_fix_jobs=0 missing_branch=6 missing_head_before=6 missing_head_after=6
```

```sh
jq -c 'select(.type=="thread.started" or .type=="turn.completed")' state/jobs/smoke-0/events.jsonl
```

Observed output:

```json
{"type":"thread.started","thread_id":"01a13eab-f90f-72e1-aefa-8a585048f968"}
{"type":"turn.completed","usage":{"input_tokens":19615,"cached_input_tokens":12928,"cache_write_input_tokens":0,"output_tokens":5,"reasoning_output_tokens":0}}
```

This first-page GraphQL probe was also run; it is not a complete pagination implementation:

```sh
gh api graphql -f query='query { repository(owner:"byronxlg",name:"unattended") { pullRequests(first:1,orderBy:{field:CREATED_AT,direction:DESC}) { nodes { number headRefName headRefOid reviews(first:100) { nodes { id state submittedAt author { login } commit { oid } } pageInfo { hasNextPage endCursor } } comments(first:100) { nodes { id body createdAt author { login } } pageInfo { hasNextPage endCursor } } reviewThreads(first:100) { nodes { id isResolved isOutdated resolvedBy { login } comments(first:100) { nodes { id body createdAt author { login } commit { oid } } pageInfo { hasNextPage endCursor } } } pageInfo { hasNextPage endCursor } } } } } }'
```

Observed output, exit 1:

```text
error connecting to api.github.com
check your internet connection or https://githubstatus.com
```

The shell could not reach GitHub; sandbox networking may be responsible. No live PR, token-permission result or successful GraphQL execution was established. Public documentation loaded through web retrieval.

For the one-day spike, the supervisor supplies one isolated build worktree and small fixture records. Run these read-only probes at dispatch and completion, with `worktree` constrained inside this repository; retain their outputs as fixture evidence:

```sh
git -C "$worktree" rev-parse --show-toplevel --git-common-dir HEAD
git -C "$worktree" symbolic-ref --quiet --short HEAD
GIT_OPTIONAL_LOCKS=0 git -C "$worktree" status --porcelain=v1 --untracked-files=normal
git -C "$worktree" merge-base --is-ancestor "$before" "$after"
git -C "$worktree" rev-list --reverse "$before..$after"
```

Before squash, read `gh api --paginate "repos/byronxlg/unattended/pulls/$pr_number/commits"` and `gh api "repos/byronxlg/unattended/pulls/$pr_number"`; repeat the PR read after merge. The spike never merges, rebases, launches paid sessions or reads private session directories itself.

Fixture acceptance matrix, with symbolic commit identities rather than invented observed SHAs:

| Fixture | Input and required verdict |
| --- | --- |
| `isolated-squash.json` | Session moves A→B→C; captured PR contains B/C; merge is S. Link B/C exactly through the receipt and PR snapshot, never claim S was emitted by the session |
| `resume-noop.json` | Two invocation IDs share a session ID; second has unchanged HEAD. Preserve both invocations without duplicating commits or usage |
| `reuse-fork.json` | Same branch name in different repository identities or lifetimes. Do not join by name alone |
| `shared-dirty-rewrite.json` | Overlapping writers, dirty input or a non-ancestor ending HEAD. Return ambiguous/incomplete unless explicit transition evidence settles it |
| `agent-comments.json` | Two agent markers on one SHA, a later reviewed SHA, an ordinary finding plus resolution marker, shared GitHub login. Count two rounds; identity comes from linked receipts |
| `unknown-human.json` | Resolved thread but an uncovered branch interval. Return unknown autonomy, regardless of resolver |
| `ci-pagination.json` | Failed attempt 1, successful attempt 2, synthetic merge SHA and a second API page. Preserve failure and all pages; truncated history returns unknown |

A proposed `product/tests/test_spike.py` should replay that matrix via `uv run --project product --with pytest pytest -q product/tests/test_spike.py`. Gate: zero falsely asserted exact joins; every positive fixture links; every negative fixture explains its uncertainty. Record live coverage separately. If no real build receipt is available, report fixture feasibility only and leave the instrumentation gate open.

## Open questions for the supervisor

1. Accept `pr-evidence` as the shared attribution/outcome library, with `bin/metrics` owning lab aggregation and publishing?
2. Require exclusive worktree assignment and receipt capture before every build/fix invocation and before squash cleanup?
3. Accept distinct reviewed head SHAs as rounds, with both agent assessments recorded separately?
4. Require versioned review/finding/resolution markers when assessments are posted as ordinary PR comments?
5. Replace the assumed autonomous-resolution claim with attested, human-involved and unknown categories?
6. Accept per-head first-attempt CI plus a separately named initial-head PR metric?
7. Can the next authorized build provide one real Codex receipt and one supplied Claude hook receipt for the spike?

## The case against

This may be lab instrumentation with a reusable interface rather than a twelve-day product. Scott Logic's [capture.mjs](https://raw.githubusercontent.com/amjones-scottlogic/AnthropicSDLCExample/main/.claude/skills/capture-metrics/capture.mjs) already provides branch-based Claude usage and PR metrics in dependency-free JavaScript. The extra value here depends on maintaining receipts, snapshots and review conventions that users may decline to adopt. Historical coverage may stay poor, and no API can prove absence of human edits under shared credentials. If a wrapper patch and a small `bin/metrics` helper answer the lab's questions, a separate product would add maintenance without enough benefit.

## Sources

- Local selection and format: `intent/README.md`, `intent/lab-metrics/intent.md`, `intent/research/review-2026-10-16.md`.
- Local research: `intent/research/sdlc-telemetry.md`, sections A/B and candidate 1; `intent/research/landscape-2026-10-15.md`, section B and niche 2.
- Inspected implementation: `bin/codex-run`, `state/ledger.jsonl`, `state/jobs/smoke-0/events.jsonl`, `state/jobs/research-sdlc-telemetry-d1/events.jsonl`, `state/jobs/candidate-pr-evidence-d1/prompt.md`.
- Local operating contract: `docs/metrics.md`, `prompts/supervisor.md`, `.github/workflows/ci.yml`, `.github/workflows/pages.yml`.
- Primary external references, retrieved for this draft: GitHub GraphQL/REST documentation, Claude hook documentation and Scott Logic source, linked beside the claims they support.