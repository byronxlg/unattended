# Lab metrics implementation plan

## Scope and evidence

Implement `intent/lab-metrics/intent.md`, with Supervisor decisions taking precedence, and every row of `docs/metrics.md`. Deliver one lab-tooling change on `change/lab-metrics`. Do not modify product code, source ledgers, posts or prompts. Commit in the assigned worktree; do not push.

The inspected state contains 35 Codex jobs, 54 ticks, two changes and one mistake record. Fleet Audit has five PRs, 11 attempts and seven `kind: fix` jobs. Its increments make change-level and PR-level measurements materially different.

The three requested GitHub probes were each attempted once and returned `error connecting to api.github.com`. The check-runs probe used `5c7ab2bc8388fcfda570a059ed3f1840b369a44d`, the local remote-tracking head for PR 5's branch, corroborated by the ledger. Its live head and actual API response shapes were not shown. Doppler discovery failed with `Token not found in system keyring`. API fixtures must therefore be labelled synthetic until verified against authenticated responses.

## Files and layout

- `bin/metrics`: executable uv inline script, Python >=3.12, sole dependency `pyyaml>=6`; resolve repository root from the script path, add it to the import path, then call `lab_metrics.cli.main`.
- `lab_metrics/__init__.py`: package marker.
- `lab_metrics/models.py`: plain dataclasses and normalized record contracts.
- `lab_metrics/sources.py`: local readers, git subprocesses and bounded GitHub reads.
- `lab_metrics/compute.py`: pure indicator calculations.
- `lab_metrics/render.py`: deterministic JSON serialization and escaped HTML.
- `lab_metrics/cli.py`: argument handling, orchestration, file writing and summary.
- `pyproject.toml`: root Python >=3.12 project with PyYAML only and no package build requirement; `uv.lock`: small generated dependency lock for root tests.
- `pytest.ini`: retain existing exclusions and add repository-root Python import path.
- `tests/test_metrics_sources.py`, `tests/test_metrics_indicators.py`, `tests/test_metrics_output.py`, `tests/test_metrics_integration.py`: root-collected tests.
- `tests/fixtures/metrics/README.md`: provenance, source commit and line/job identifiers, synthetic case labels and expected answers.
- `tests/fixtures/metrics/real/ledger.jsonl`, `ticks.jsonl`, `changes.yaml`, `mistakes.jsonl`: small verbatim copies of selected state records.
- `tests/fixtures/metrics/synthetic/ledger.jsonl`, `ticks.jsonl`, `changes.yaml`, `mistakes.jsonl`, `evals.jsonl`, `github.json`, `git_history.json`: explicitly synthetic edge cases, including future evidence contracts below.
- `.github/workflows/pages.yml`: generate metrics before blog build.
- `.github/workflows/ci.yml`: correct the root-test presence guard described below.
- `site/data/metrics.json`: generated, already ignored through `site/`; never commit it.
- `intent/lab-metrics/plan.md`: supervisor installs this document; record implementation departures here.

## Source contracts

Use `SourceResult[T]` with fields `available`, `reason`, `data`, `skipped`, `warnings`. Reasons are stable codes with controlled descriptions, never raw stderr. Missing optional evidence differs from an empty, readable source. Retain valid records when skipping malformed lines; attach counts to affected indicators.

Signatures:

- `read_head(root: Path) -> Head`: fields `sha`, `committed_at`.
- `read_artifact_history(root: Path, slugs: list[str]) -> SourceResult[list[ArtifactCommit]]`.
- `read_jobs(path: Path) -> SourceResult[list[Job]]`.
- `read_ticks(path: Path) -> SourceResult[list[Tick]]`.
- `read_changes(path: Path) -> SourceResult[list[Change]]`.
- `read_mistakes(path: Path) -> SourceResult[list[Mistake]]`.
- `read_evals(path: Path) -> SourceResult[list[EvalResult]]`.
- `read_github(repo: str, pr_numbers: list[int], deadline: float) -> GitHubSnapshot`.
- `compute(snapshot: Snapshot) -> list[Indicator]`.
- `render_document(head: Head, indicators: list[Indicator], diagnostics: dict) -> bytes`.
- `main(argv: list[str] | None = None) -> int`.

`ArtifactCommit` fields: `slug`, `artifact`, `sha`, `committed_at`, `added`, `order`. Read first additions with `git log HEAD --reverse --topo-order --format=%H%x09%cI --diff-filter=A -- <path>`. Read all touches separately with the same explicit format and path; deduplicate hashes. Use first reachable addition, not filesystem mtime or most recent edit. Count subsequent touches using history order, excluding the boundary commit. Measure elapsed time with commit timestamps; flag negative intervals. No fetching or checkout.

`Job` fields: `id`, `kind`, `change`, `started`, `ended`, `duration_s`, `rc`, `killed`, `thread_id`, `usage`, `rate_limits`. Usage retains `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens`; rate windows retain `used_percent`, `window_minutes`, `resets_at` for primary and secondary. Never extract metrics from `last_message`.

`Tick` fields: `ts`, `reasons`, `jobs_running`, supervisor `ran`, `rc`, `error`, `cost_usd`, `turns`, `duration_ms`. Do not parse supervisor `result` prose.

`Change` fields: `slug`, `kind`, `started`, `outcome`, `attempts`, `plan_match`, `origin`, `prs`. YAML timestamps may already be datetime objects; normalize those and timestamp strings identically. Use explicit `prs` joins only; never infer slug from branch names.

`Mistake` fields: `ts`, `agent`, `change`, `mistake`, `occurrences`, `correction`. Preserve occurrence strings for deduplication, not chronology inference.

Optional future evidence contracts, supported by readers and synthetic tests without changing producers:
- Change `regressions`: events with `id`, `detected_at`, `caught_in` (`ci` or `after_merge`); `incident_ids`: stable incident identifiers.
- Eval records: `ts`, `eval_id`, `passed` boolean; optional `incident_id`, `incident_at`, `permanent_at`.
- Tick `signals`: records with `id`, `kind` (`band_breach`), `change`, `detected_at`.
Absent fields yield “not shown”; never synthesize evidence from narrative notes.

Blank JSONL lines are ignored. Invalid JSON, non-object rows and records missing mandatory identity fields are skipped and counted. Invalid optional values exclude only the affected calculation. Reject booleans as numeric values, nonfinite numbers and negative durations. Deduplicate jobs by ID; conflicting duplicates are excluded with diagnostics. Unreadable required files or malformed YAML fail the command.

## GitHub reader

Use GET requests through `gh api` subprocess argument lists, repository fixed to `byronxlg/unattended`. Each list request uses `per_page=100`, `--paginate --slurp`; flatten page arrays or each page's named collection. Never silently use only the first page.

Named readers and retained fields:

- `read_prs(repo, deadline) -> SourceResult[list[PullRequest]]`: `/repos/{repo}/pulls?state=all`; retain `number`, `created_at`, `closed_at`, `merged_at`, `head.sha`, `merge_commit_sha`, `user.login`, `body`.
- `read_reviews(repo, number, deadline) -> SourceResult[list[Review]]`: `/repos/{repo}/pulls/{number}/reviews`; retain `id`, `submitted_at`, `state`, `user.login`, `body`, `commit_id`.
- `read_review_comments(repo, number, deadline) -> SourceResult[list[ReviewComment]]`: `/repos/{repo}/pulls/{number}/comments`; retain `id`, `created_at`, `user.login`, `body`, `pull_request_review_id`, `in_reply_to_id`.
- `read_checks(repo, sha, deadline) -> SourceResult[list[CheckRun]]`: `/repos/{repo}/commits/{sha}/check-runs?filter=all`; flatten `check_runs`; retain `id`, `name`, `head_sha`, `status`, `conclusion`, `started_at`, `completed_at`, `app.slug`, `check_suite.id`.
- `read_workflow_runs(repo, workflow, deadline) -> SourceResult[list[WorkflowRun]]`: `/repos/{repo}/actions/workflows/{workflow}/runs`; call for `ci.yml` and `pages.yml`; flatten `workflow_runs`; retain `id`, `run_attempt`, `head_sha`, `event`, `status`, `conclusion`, `created_at`, `run_started_at`, `updated_at`, `html_url`.
- `read_run_jobs(repo, run_id, deadline) -> SourceResult[list[WorkflowJob]]`: `/repos/{repo}/actions/runs/{run_id}/jobs?filter=all`; flatten `jobs`; retain `id`, `name`, `status`, `conclusion`, `started_at`, `completed_at`.
- `read_gates(repo, deadline) -> SourceResult[list[GateIssue]]`: `/repos/{repo}/issues?state=all&labels=needs-byron`; discard PR objects; retain `number`, `created_at`, `closed_at`, `labels[].name`, `body`.

Fetch PR details only for explicitly linked PRs, checks once per unique head, jobs only for Pages runs. Cache responses in memory. Deduplicate IDs and sort explicitly; do not rely on API ordering. Missing required page/envelope fields mark the source unavailable rather than accepting a partial denominator.

Use a 45-second global GitHub budget and at most four concurrent subprocesses, each bounded by the smaller of eight seconds and remaining budget. No retries or rate-limit sleeps. Missing executable, authentication failure, network failure, timeout, permission denial and rate exhaustion return unavailable markers. Stop scheduling after a global connectivity/authentication failure. A truncated pagination request invalidates that entire source.

Every indicator dependent on an unavailable GitHub source has `available: false`, `value: null`, `n: 0` and a reason. Independent local indicators still render. Never substitute an empty API response for failure.

## Calculation conventions

Unless specified otherwise, summarize durations and per-change counts with arithmetic means. Percentages are 100 times numerator divided by denominator; `n` is the denominator. Numeric zero is valid evidence. Empty eligible samples produce `value: null`, `n: 0`, `available: true`, note `no data (n=0)`. Missing instrumentation produces `available: false`, note `not shown: <reason>`.

Use all readable local records and the fetched GitHub snapshot. `generated_at` identifies the HEAD commit time, not a claim that later GitHub events are excluded. Closed unresolved gates use that timestamp as their deterministic censoring point; flag events later than it.

Each subsection below corresponds to one specification row, in table order. Compound rows emit separate scalar indicators with separate sample sizes. Units are explicit; preserve all rows even when unavailable.

### 1. Plan: conversation to intent
Mean first intent addition time minus `changes.started`, in hours; `n` is valid timestamp pairs. Missing starts or additions give no eligible sample. `started` is the recorded conversation proxy.

### 2. Plan: intent survival
Accepted outcomes are `accepted`, `building`, `in_review`, `merged`, `reverted`; denominator adds `closed`, excludes `open`. Return accepted/decided as percent, `n` decided changes. No decided outcomes means no data.

### 3. Plan: intent edits after specification
Count distinct intent-touch commits after first spec addition per slug; mean commits/change, `n` slugs with a spec and intent history. Zero edits counts. Without a per-slug spec, including lab-metrics, no eligible sample; do not substitute `docs/metrics.md`.

### 4. Design: intent to specification
Mean first spec addition minus first intent addition, hours; `n` valid pairs. Missing either artifact means no eligible sample. This measures committed artifacts, not approval timestamps.

### 5. Design: requirements rework
Mean distinct spec-touch commits after first plan addition, commits/change; `n` slugs with both artifacts. Zero rework counts; missing boundaries mean no eligible sample.

### 6. Build: first implementation pass
Percent of `outcome: merged` changes with `attempts == 1`, among merged changes with integer attempts >=1; `n` eligible changes. No valid attempts means no data. Keep the specified change-level formula despite multi-increment plans.

### 7. Build: plan approval to merge
Mean last linked PR merge minus first plan addition, hours/change; `n` merged changes whose listed PRs are all merged and whose plan exists. Missing pairs mean no data. First plan commit proxies approval; last PR completes a multi-PR change.

### 8. Build: rework cycles
For each change with attempts >=1, calculate `attempts - 1 + distinct fix-job count`; report mean cycles/change and component counts, `n` eligible changes. Include failed/killed fix jobs as attempted work. No valid attempts means no data. Fleet Audit's literal result is 17; note possible double counting and planned-increment inflation.

### 9. Build: plan match
Percent true among explicit boolean `plan_match` on merged changes; `n` recorded verdicts. Null is unknown, not false. No verdicts means no data. Do not infer semantic agreement from diffs.

### 10. CLAUDE.md: repeated mistakes
Sum `max(distinct occurrence count - 1, 0)` across valid mistake records; unit repeat occurrences, `n` recorded mistake classes. The real class contributes one repeat. Empty ledger means no data; a class with one occurrence contributes zero. Coverage is recorded mistakes only.

### 11. Parallel: concurrency with review quality
Sweep valid `[started, ended)` job intervals, ending jobs before starting jobs at equal timestamps. Report peak jobs and time-weighted mean jobs over the union of active intervals; `n` valid jobs. No intervals means no data. Also emit review-quality-held as unavailable: structured quality evidence is not shown; overlap alone proves no quality claim.

### 12. Parallel: weekly merges alongside rework
Count distinct linked merged PRs by Pacific/Auckland ISO week; `n` merged PRs, unit PRs/week. Also report distinct completed changes and mean row-8 rework for changes completed in each week, with their own `n`. No merges means no data. Include year in week keys and do not multiply one change's attempts by its PR count.

### 13. Test: first-pass CI success
For each linked PR with a ledger build job for its change, group head check runs by `(app.slug, name)` and select earliest `(started_at, id)` per group. A PR passes only if every selected completed check concludes `success`; terminal non-success counts as failure, pending groups exclude the PR. Percent passing PRs; `n` evaluable PR heads. Empty checks mean no data. Final stored PR head is a proxy: original implementation-head CI is not shown.

### 14. Test: review time
Mean first submitted, non-pending review time minus PR creation, minutes; `n` valid PR/review pairs. Missing reviews mean no data. Report submitted-review latency as a proxy: supervisor identity and review effort are not reliably recorded. Reviews embedded in the creation body have no independent submission timestamp and are excluded.

### 15. Test: change failure rate
Among merged or reverted changes with all linked merge times, count changes reverted or having an attributed fix job starting strictly after their final merge. Percent failed; `n` eligible changes. No merged cohort means no data. This conservative change-level proxy cannot identify which earlier increment caused a later fix; do not classify pre-completion fixes as escaped defects.

### 16. Evals: pass rate and incident-to-eval
Pass rate is true results/boolean results, percent, `n` results, with daily rates by `ts`. Incident-to-eval is mean first permanent timestamp minus incident timestamp for distinct incident IDs, hours, `n` linked incidents. Missing `evals/results.jsonl` is unavailable; present empty file means no data. Never treat pytest results as eval records.

### 17. Evals: regressions caught before and after merge
Deduplicate structured regression events by ID; report CI and after-merge counts and CI share of their total, `n` classified events, units events and percent. Empty explicit collections mean no data; absent collections are unavailable. Notes are not a classifier.

### 18. Deploy: time to first review
Mean earliest submitted review or root review-comment timestamp minus PR creation, minutes; `n` PRs with a valid event. No events means no data. Include the note that same-supervisor-run creation and review can yield minutes by construction; this does not establish independent response speed.

### 19. Deploy: comments resolved without human branch edits
Emit the exact indicator as unavailable: REST comments do not establish thread resolution or branch-editor identity. Also emit the lab's stated agent-resolution proxy: merged PRs with root review comments / all linked PRs with root review comments, percent, `n` commented PRs. No comments means no data. Label explicitly as an assumption that merged comments were agent-resolved, not verified human-free editing.

### 20. Deploy: defects caught versus escaped
Emit exact defect counts as unavailable because review findings lack a structured severity/identity contract. Provide separately labelled activity proxies: root review comments submitted before merge and attributed fix jobs after final change merge, units comments and jobs; `n` inspected PRs and merged changes respectively. No eligible cohorts means no data. Do not equate comments, fixes and unique defects.

### 21. Gates: approval waiting
Per `needs-byron` issue, closed duration is `closed_at - created_at`, hours; mean closed wait has `n` closed issues. Open issues get censored ages to HEAD time with their own `n`. No issues means no data. Issue lifetime proxies gate wait because label-addition and distinct gate events are not recorded.

### 22. CI/CD: failures triaged without paging
For terminal failed CI runs, detect explicit run URLs in gate issue bodies. Report unpaged failure share as a proxy: failures without a linked gate / failures, percent, `n` failed runs. Failure conclusions are `failure`, `timed_out`, `action_required`, `startup_failure`; exclude cancellation. No failures means no data. Exact triaged-without-human share remains unavailable because absence of a page does not establish triage.

### 23. CI/CD: DORA
Deployment frequency counts distinct successful Pages `deploy` jobs per NZ day; summarize deployments/calendar day between first and last observed Pages run dates, including zero days; `n` observed days. No runs means no data.
Lead time is first successful deploy completion for an exact PR `merge_commit_sha` minus `merged_at`, hours; `n` matched PRs. No exact match means no data; never match merely by nearest time.
Change failure rate reuses row 15, explicitly labelled a change-level proxy, with the same denominator.
Restore time is mean first successful deploy completion after the start of each failed-deploy episode, measured from first failed deploy completion, hours; `n` closed episodes. Consecutive failures form one episode; open episodes are censored and excluded. No completed episodes means no data. Pipeline recovery is not evidence of production service restoration.
Here Deploy is Pages deployment. Successful workflow builds without a successful `deploy` job are not deployments; cancelled runs are not incidents.

### 24. Maintain: breach to intent
Mean first intent addition minus structured band-breach detection, hours; `n` uniquely linked signals with nonnegative intervals. Missing structured signals means unavailable; present empty signals mean no data. Existing `idle`, `heartbeat` and `job_done` reasons are not band breaches.

### 25. Maintain: findings to fixes and repeat incidents
Percent `origin: finding` changes with `outcome: merged` among decided finding changes (`merged`, `closed`, `reverted`), `n` decided findings. No findings means no data; pending findings are excluded and counted in the note.
Repeat incidents count later finding changes sharing explicit incident IDs, unit repeat incidents, `n` distinct IDs. Missing incident IDs means unavailable; never infer recurrence from similar prose.

## Cost and capacity

Codex: sum each reported usage field separately per job and NZ completion day; `n` jobs reporting that field. Total tokens are input plus output, never plus cached input or reasoning output again. Missing usage is unknown; explicit zero remains zero. Label totals as reported ledger usage because resumed-thread accounting may include overlapping context.

Weekly window: choose the window whose `window_minutes == 10080`, from primary or secondary. For each NZ day report the latest `(ended, id)` snapshot's `used_percent` and `resets_at`; `n` valid snapshots. Never sum percentages or treat reset drops as negative consumption. No weekly snapshots means no data.

Supervisor: retain each `ran: true` tick's cost and turns, keyed by timestamp and source line; report sums per NZ completion day and means per run, with separate `n` for each non-null field. Include failed runs and explicit zero cost; exclude skipped ticks. Units USD and turns. No reported values means no data. Use six decimal places for USD.

Wall time: mean final linked merge minus `started`, hours/change, `n` completed valid pairs; emit per-change values. Also report sum of valid job durations by change as job-seconds, clearly distinct from elapsed wall time. Open changes have no completed wall-time sample. Null-change jobs remain in total cost and concurrency, not per-change wall time.

## Output and CLI

Top-level keys: `generated_at`, `head_commit`, `indicators`, `diagnostics`, `html`. `generated_at` is HEAD's committer timestamp in UTC ISO format. Every indicator has `stage`, `kind`, `name`, `definition`, `value`, `unit`, `n`, `available`, `note`, `series`. Daily series entries have `date`, `value`, `n`, `available`, `note`; weekly entries use `week`. Use empty series where none exists.

Provide daily series for completed durations, review latencies, rates with timestamped events, mistakes, concurrency, deployments, evals and costs. Do not invent dated series for mutable outcomes without transition timestamps. Calculate daily rates from daily numerators and denominators, not averages of percentages.

Serialize sorted object keys, fixed ordering of indicators and samples, UTF-8, two-space indentation and a trailing newline. Round ordinary floats to four decimals and USD to six; reject NaN and normalize negative zero. Determinism means identical bytes for identical HEAD, local records and captured GitHub responses; live GitHub may change independently.

HTML contains one heading and table per stage plus a cost table. Columns: indicator, definition, value/unit, n, note. Use only existing blog styling and ordinary semantic HTML; no scripts, inline styles, external assets or full-page wrapper. Escape every dynamic string and normalize banned characters before rendering. Display unavailable reasons and `no data (n=0)` explicitly.

`bin/metrics` writes atomically to `site/data/metrics.json` and prints `metrics: N indicators, U unavailable, S skipped`. `bin/metrics --json -` prints identical JSON bytes to stdout without writing; send diagnostics to stderr. Drop `--check`: the file is generated in Pages, not committed. Determinism is verified against frozen inputs in tests.

## Tests

In `tests/test_metrics_indicators.py`, implement these named tests with explicit numeric expected results:
- `test_conversation_to_intent`, `test_intent_survival`, `test_intent_changes_after_spec`, `test_intent_to_spec`, `test_spec_rework`: boundary commits, zero edits, missing artifacts, accepted/open/closed denominators.
- `test_first_pass_merge`, `test_plan_to_final_merge`, `test_rework_cycles`, `test_plan_match`: multi-PR completion, seven fix jobs plus ten attempts-derived cycles, unknown verdict exclusion.
- `test_repeated_mistakes`, `test_concurrent_jobs`, `test_weekly_merges_and_rework`: deduplicated occurrences, touching intervals, time weighting, ISO-year boundary and change/PR distinction.
- `test_first_pass_ci`, `test_review_time`, `test_change_failure_rate`: earliest check versus successful rerun, pending checks, missing reviews and pre-final/post-final merge fixes.
- `test_eval_pass_rate_and_latency`, `test_regression_detection`: pass denominator, distinct incident latency and classified event shares.
- `test_first_review`, `test_agent_resolution_proxy`, `test_defect_proxies`, `test_gate_wait`: earliest comment/review, exact metrics unavailable, pre/post-merge separation and censored open gates.
- `test_pipeline_triage_proxy`, `test_dora`: linked run URLs, exclusions, exact merge SHA, successful deploy job, daily zeros and red-red-green episode.
- `test_breach_to_intent`, `test_findings_and_repeat_incidents`: explicit signal linkage, missing instrumentation, pending findings and repeat IDs.
- `test_codex_tokens`, `test_weekly_window`, `test_supervisor_cost_and_turns`, `test_wall_time`: component accounting, latest snapshot/reset, skipped/null/zero runs and elapsed versus summed job time.

In `tests/test_metrics_sources.py`: `test_real_fixture_shapes`, `test_git_first_addition_and_touches`, `test_github_pagination_and_envelopes`, `test_github_unavailable`, `test_github_deadline`, `test_malformed_line_skipped_and_counted`, `test_duplicate_job_ids`, `test_optional_evidence_missing`. Assert unavailable behavior for missing gh, unauthenticated, offline, permission, timeout and partial-page failures without raising.

In `tests/test_metrics_output.py`: `test_deterministic_bytes` runs twice with reordered frozen inputs; `test_html_safety` checks escaping, no script/style, no em dash or emoji; `test_all_spec_rows_present` checks coverage; `test_empty_and_unavailable_differ`; `test_nz_day_and_dst` covers midnight and the 2026-09-27 spring-forward transition; `test_cli_stdout_and_generated_file` compares bytes and stdout purity.

In `tests/test_metrics_integration.py`: `test_real_state_under_60_seconds` uses real local state and stubbed GitHub, measures the whole pipeline with a monotonic clock and asserts under 60 seconds; `test_pages_workflow_contract`, `test_ci_collects_root_tests`, `test_blog_consumes_fragment` verify integration using temporary output directories. Tests never write real state or require live GitHub.

## Pages and CI

Add a `Generate metrics` step after setup/check-posts and before `bin/blog build`, running `bin/metrics` with `GH_TOKEN: ${{ github.token }}`. Retain full checkout history and existing permissions. Expected GitHub outages produce a valid partial report and allow deployment. Unexpected computation, serialization or write errors fail the build, preventing publication of misleading metrics.

The existing CI guard passes both root and `product/tests` globs to one `ls`; an absent product glob can suppress root tests. Replace it with an independent root-test existence check. Keep the separate Fleet Audit job commands and pytest exclusions unchanged.

## Concerns

- Pagination and rate limits: bounded, paginated, cached reads; partial sources become unavailable, never biased denominators. Live default-token access and response shapes remain to be verified.
- Same-run reviews: report measured latency with the explicit construction artifact; do not claim independent review speed or effort.
- NZ days: use `zoneinfo.ZoneInfo("Pacific/Auckland")`, never a fixed offset. DST starts 2026-09-27; elapsed durations use UTC, grouping uses NZ civil dates.
- Fix attribution: only exact `kind == "fix"` and exact non-null change slug count; ID suffixes and prose do not. Attempts plus fixes follows the spec literally despite overlap. Post-merge failure uses final change merge to avoid misclassifying later increments.
- Null changes: retain in global cost/concurrency; exclude from joins and report unattributed job count.
- Missing evidence: unsupported exact indicators remain visible, with separately named proxies and explicit future field contracts. Never convert absence into success.
- Mutable GitHub versus HEAD time: deterministic serialization is conditional on the same captured API inputs; commit time is a reproducible generation anchor, not API observation time.
- Quality and causality: neither overlap, a green check nor merge proves review quality, agent-only editing or absence of defects.
- Runtime: 45-second network budget leaves local processing headroom. Stubbed runtime tests do not prove live Actions latency; verify a real workflow run during supervisor review.

## Risks and rejected alternatives

Riskiest step: correlating multi-increment changes, final PR heads, fixes and deployments without overstating causality. Resolve with explicit joins, conservative boundaries, independently named proxies and fixtures demonstrating misleading cases.

Reject scraping prose for findings, approvals or incidents: truncated narratives and inconsistent timestamps cannot establish stable denominators.
Reject treating missing GitHub data as empty successful results: it would turn outages into false zero failures.
Reject committing metrics JSON or using wall-clock generation time: generated Pages output avoids stale-file churn and supports reproducible tests.

## Build order and proving commands

- [ ] Add package, dependency metadata and provenance-labelled fixtures. Prove with `uv run --with pytest pytest -q tests/test_metrics_sources.py -k real_fixture_shapes`; expect `1 passed`.
- [ ] Implement readers, normalization and bounded GitHub client. Prove with `uv run --with pytest pytest -q tests/test_metrics_sources.py`; expect summary containing `passed`, no failures.
- [ ] Implement every indicator and cost calculation. Prove with `uv run --with pytest pytest -q tests/test_metrics_indicators.py`; expect summary containing `passed`, no failures.
- [ ] Implement output and CLI. Prove with `uv run --with pytest pytest -q tests/test_metrics_output.py`; expect summary containing `passed`, no failures.
- [ ] Wire Pages and repair CI test collection. Prove with `uv run --with pytest pytest -q tests/test_metrics_integration.py`; expect summary containing `passed`, including runtime assertion.
- [ ] Run `bin/metrics` and `bin/blog build`; expect `metrics: N indicators, U unavailable, S skipped` and `built N posts into site/`. Inspect the metrics page and unavailable notes; numeric counts depend on current inputs.
- [ ] Run `bin/lint`; expect `lint ok (N text files)`. Run the full root `uv run --with pytest pytest -q`; expect summary containing `passed`, no failures. Record actual output, commit only named task files and leave pushing to the supervisor.
## Supervisor decisions (2026-10-16, plan accepted with these amendments)

1. Drop the "optional future evidence contracts" for change `regressions`, `incident_ids` and
   tick `signals`. Rows 17, 24 and the repeat-incident half of 25 emit `available: false`
   with the note "not shown: no structured source yet". Keep the `evals/results.jsonl` reader
   with fields `ts`, `eval`, `passed` and optional `incident_at`; incident-to-eval is the first
   result `ts` for an eval minus its `incident_at`. No synthetic fixtures for dropped fields.
2. The root `pyproject.toml` carries `[tool.uv] package = false` and no build system; pytest
   configuration stays in `pytest.ini`. Invariant: `bin/lint`, `bin/blog build` and
   `bin/codex-run` keep running unchanged as inline-metadata scripts (uv ignores the project
   for those); prove with `bin/lint` after the pyproject lands.
3. At most two concurrent `gh` subprocesses, not four. Everything else in the GitHub reader
   section stands.
4. The HTML fragment uses `h2` per stage and for the cost block; `bin/blog` already writes the
   page `h1`.
5. The fix to the CI test guard is in scope (it suppresses root tests when `product/tests`
   has no match, since `ls` exits non-zero on any missing argument).
6. Add one line for `lab_metrics/` to the Layout section of `CLAUDE.md` in the same change.
7. Pattern named up front for the implementer and both reviewers: every value read from a
   ledger, YAML file, git or the API is untrusted. Timestamp parsing, numeric coercion and
   timezone conversion must degrade to a diagnostic (skipped, counted, named in `diagnostics`),
   never raise; and every shape `compute` emits must be accepted by `render_document`, proved
   by tests that run the two together on the synthetic fixtures.
