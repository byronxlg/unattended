# Plan brief: lab metrics (Build stage, plan mode)

You are the engineer in the unattended lab (read AGENTS.md). This job writes plan.md for the
lab change `lab-metrics`. Your sandbox is read-only: your final message IS the deliverable.
The supervisor copies it verbatim into intent/lab-metrics/plan.md, so write one complete
markdown document, title on the first line, nothing before or after it, under 250 lines.
Write for an engineer who never saw this conversation and will implement from the plan alone
in a fresh context.

Read first, in this order: intent/lab-metrics/intent.md (the "Supervisor decisions" section
overrides the body where they differ), docs/metrics.md (the spec: every row of the table is a
requirement), docs/playbook.md, bin/blog (how site/data/metrics.json is consumed; lines 89 to
94), bin/lint (what CI enforces, and the ledger shapes it already checks), bin/codex-run
(lines 130 to 140: the ledger record it writes), bin/tick (lines 108 to 126: the ticks.jsonl
record), state/ledger.jsonl, state/ticks.jsonl, state/changes.yaml, state/mistakes.jsonl
(real data; read the whole files, they are small), .github/workflows/ci.yml and pages.yml,
pytest.ini, REVIEW.md. Run `gh pr list --state all --json number,createdAt,mergedAt,headRefOid`
and `gh api repos/byronxlg/unattended/pulls/5/reviews` and
`gh api repos/byronxlg/unattended/commits/<head sha of PR 5>/check-runs` once each to see the
real shapes; do not write files, do not run anything that mutates.

## What the plan must contain

1. Layout: where the importable module lives, how `bin/metrics` (uv inline script, Python
   3.12, PyYAML only) imports it, where tests live (tests/test_metrics*.py, collected by the
   root `uv run --with pytest pytest -q`), fixture layout for the fixture ledgers the tests use
   (small copies of real lines from state/, plus labelled synthetic ones). Name every file.
2. Data sources as functions with signatures: git log reader (first commit touching
   intent/<slug>/<artifact>.md, from `git log --format --diff-filter=A`), GitHub reader
   (`gh api` calls, each one named, paginated, and the exact fields kept), ledger readers.
   Each reader returns plain dataclasses or dicts; name the fields. GitHub readers must
   return an "unavailable" marker when `gh` is missing, unauthenticated or offline, and
   every indicator built on them then reports `available: false` with the reason.
3. One section per indicator in docs/metrics.md, in table order: the formula, the inputs, the
   sample size n, what "no data" means for it, and the unit. Where the lab's data cannot
   support the playbook definition yet, say exactly how it degrades (for example the Deploy
   stage here is the Pages deploy run of the merge commit). The cost and capacity block at
   the end of docs/metrics.md is required too: Codex tokens and weekly window per NZ day
   (ledger usage and rate_limits), supervisor cost_usd and turns per run and per day
   (ticks.jsonl), wall time per change.
4. Output shape of site/data/metrics.json: top-level keys (generated_at, head commit, a list
   of indicators each with stage, kind, name, definition, value, unit, n, available, note,
   and a per-day series where one exists), and the `html` fragment: one table per stage plus
   the cost block, no scripts, no styles beyond what bin/blog already ships. Deterministic
   for the same inputs (sorted keys, fixed float precision, generated_at from the HEAD
   commit time, not wall clock).
5. CLI: `bin/metrics` writes the JSON and prints a short text summary; `bin/metrics --check`
   recomputes and exits non-zero if the committed file would change (name whether the file
   is committed or generated; the supervisor's intent says it is generated in Pages, so say
   what `--check` is for or drop it). `bin/metrics --json -` to stdout for posts.
6. Tests: name each test function and what it asserts, one per indicator formula at least,
   plus: unavailable GitHub degrades without raising; malformed ledger line is skipped and
   counted; determinism (two runs, identical bytes); the html fragment contains no em dash
   or emoji; runtime under 60 s against the real state/ with GitHub stubbed.
7. The pages.yml change: a step that runs `bin/metrics` before `bin/blog build` with
   `GH_TOKEN: ${{ github.token }}`, and what happens to the deploy if metrics fails (decide:
   fail the build, or write the file with everything unavailable; say why).
8. Build order as a checklist (`- [ ] ` items) the implementer ticks, each with its proving
   command and expected output line, finishing with `bin/lint` and the full test run.
9. `## Concerns`: every design concern you flagged and how the plan resolves it (at least:
   GitHub rate limits and pagination, the same-run time-to-first-review artefact from the
   intent, timezone for the per-day series (NZ days, Pacific/Auckland, DST on 2026-09-27),
   what counts as a "fix job in the ledger" per change, what to do with jobs whose change is
   null).
10. Risks and rejected alternatives: riskiest step, three alternatives rejected with a
    sentence each.

## Constraints

Stdlib plus PyYAML only; no GitHub library, `gh api` via subprocess. Read-only against
GitHub and git. No product code touched. No implementation code in the plan beyond
signatures, field lists and test names. No emojis, no em dashes. Humble: say "not shown"
where evidence does not reach.
