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
