# Indicators and how this lab measures them

Definitions follow the playbook (`docs/playbook.md`). "Source" says what `bin/metrics` reads:
git history of `intent/`, the GitHub API for PRs, reviews and check runs, `state/ledger.jsonl`
(every Codex job), `state/changes.yaml` (per-change outcomes the supervisor records),
`state/mistakes.jsonl`, `state/ticks.jsonl`, `evals/results.jsonl`. Leading indicators move
first and are read daily; lagging ones are read at the end and in the retrospective.

| Stage | Kind | Indicator | Source in this lab |
| --- | --- | --- | --- |
| Plan | leading | time from first conversation to a committed `intent.md` | `state/changes.yaml` `started` to first commit touching `intent/<slug>/intent.md` |
| Plan | lagging | intent survival rate: share accepted into Design rather than closed | `changes.yaml` `outcome` |
| Plan | lagging | `intent.md` changes after the first `spec.md` commit | git log counts per slug |
| Design | leading | elapsed time intent commit to spec commit | git log per slug |
| Design | lagging | `spec.md` commits after the first `plan.md` commit (requirements rework) | git log per slug |
| Build | leading | share of changes merged from the first implementation pass | `changes.yaml` `attempts` == 1 among merged |
| Build | leading | time from plan approval to merged PR | plan commit to PR `merged_at` |
| Build | lagging | rework cycles per change | `changes.yaml` `attempts` minus 1, plus fix jobs in the ledger |
| Build | lagging | merged diff still matches `plan.md` | supervisor verdict `plan_match` per change at merge |
| CLAUDE.md | leading | repeated mistakes CLAUDE.md/AGENTS.md should have caught | `state/mistakes.jsonl` |
| Parallel | leading | concurrent Codex jobs while review quality holds | ledger overlap of `started`/`ended` |
| Parallel | lagging | changes merged per week alongside rework rate | PRs merged per ISO week |
| Test | leading | first-pass CI success rate for agent-written changes | first check-run conclusion per PR head |
| Test | lagging | review time per PR | PR `created_at` to the supervisor's review submitted |
| Test | lagging | change failure rate | changes needing a `fix` job or revert after merge |
| Evals | leading | eval pass rate over time; time incident to permanent eval | `evals/results.jsonl` |
| Evals | lagging | regressions caught in CI vs in production (here: after merge) | `changes.yaml` |
| Deploy | leading | time to first review (target minutes) | PR `created_at` to first review or review comment |
| Deploy | leading | share of review comments resolved without a human touching the branch | here all comments are agent-resolved; counted per PR |
| Deploy | lagging | defects caught before merge vs escaped | review findings vs post-merge fixes |
| Gates | leading | time waiting on each approval gate | `needs-byron` issue open duration |
| CI/CD | leading | share of pipeline failures triaged without paging a human | failing runs vs `needs-byron` issues about them |
| CI/CD | lagging | DORA: deployment frequency, lead time, change failure rate, time to restore | Pages deploy runs, PR merge to deploy, fixes, red-to-green |
| Maintain | leading | time from band breach to an `intent.md` in triage | `state/ticks.jsonl` signals vs intent commits |
| Maintain | lagging | share of findings becoming merged fixes; repeat incidents | `changes.yaml` origin `finding` |

Cost and capacity, which the playbook does not list but Byron will ask about: Codex tokens and
weekly window used per day (ledger `usage`, `rate_limits`), supervisor cost and turns per run
(`ticks.jsonl`), wall time per change.
