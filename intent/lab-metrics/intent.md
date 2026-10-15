# Intent: lab metrics

Originator: the supervisor (Claude), 2026-10-15. Change kind: lab tooling.

## Problem

Byron asked for the playbook's leading and lagging indicators to be measured and shown, not
described. Today the lab records raw events (every Codex job in `state/ledger.jsonl`, every tick
in `state/ticks.jsonl`, change outcomes in `state/changes.yaml`, artifacts in `intent/`, PRs and
check runs on GitHub) but nothing turns them into the indicators in `docs/metrics.md`, and the
blog's metrics page is empty.

## Proposed outcome

`bin/metrics` computes every indicator in `docs/metrics.md` that has data, from git history, the
GitHub API (`gh api`) and the ledgers, and writes `site/data/metrics.json` with the values, the
definitions, the sample sizes and an HTML fragment the blog renders at `/unattended/metrics/`.
Indicators without data yet are shown as "no data (n=0)" rather than omitted. Daily posts quote
from it. It runs in the Pages workflow before `bin/blog build`, and locally.

## Affected users and systems

Readers of the blog; the supervisor (uses it for posts); the Pages workflow (needs `gh` auth via
`GITHUB_TOKEN` for the API reads). No product code.

## Constraints

Python with uv inline metadata, stdlib plus PyYAML only; must run in under 60 s in Actions with
the default token; read-only against GitHub; unit tests for every computation against fixture
ledgers; no emojis or em dashes in output; deterministic output for the same inputs.

## Open questions

- Cost: the supervisor's own cost per run is in `ticks.jsonl` (`cost_usd` when the harness
  reports it); Codex has no dollar figure, only tokens and the weekly window percentage. Show
  both as they are.
- Time to first review for a PR opened and reviewed by the same supervisor run will be minutes
  by construction; still report it, with a note.

## Supervisor decisions (2026-10-16, before the plan job)

1. Lab tooling, one PR on branch `change/lab-metrics`. `docs/metrics.md` is the spec for this
   change (the indicator table is the requirement list); no separate `spec.md`. Concerns go in
   `plan.md` under `## Concerns`, resolved there.
2. Tests live in `tests/test_metrics*.py` at the repo root so CI's existing step collects them
   (`pytest.ini` skips `product/` and dotdirs; CI runs `uv run --with pytest pytest -q` when
   `tests/test_*.py` exists). The computation must be importable from tests, so the script
   logic lives in an importable module and `bin/metrics` is the entry point.
3. Output contract: `site/data/metrics.json` is read by `bin/blog build`, which renders the
   `html` key as the body of `/unattended/metrics/` and falls back to a pretty-printed dump
   when that key is absent. Keep `html` as a fragment, not a page.
4. GitHub reads go through `gh api` only (the host and Actions both have `gh`); with no token
   or no network the tool still writes the file, marking GitHub-sourced indicators as
   unavailable rather than failing.
5. `bin/metrics` runs in `pages.yml` before `bin/blog build`; the PR changes that workflow.
   `GITHUB_TOKEN` with `contents: read` can read PRs, reviews and check runs on a public repo.
