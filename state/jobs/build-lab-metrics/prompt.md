# Build brief: lab metrics (one change, branch change/lab-metrics)

You are the engineer (read AGENTS.md). Implement intent/lab-metrics/plan.md in full in this
worktree. The plan was written for you by a peer who read the same files; the "Supervisor
decisions" section at the end of plan.md overrides the body where they differ, read every
decision. If you must depart from the plan, update plan.md in the same commit and say why in
your final message.

Read first: intent/lab-metrics/plan.md, intent/lab-metrics/intent.md, docs/metrics.md,
bin/blog (lines 89 to 94), bin/lint, pytest.ini, .github/workflows/ci.yml and pages.yml,
state/ledger.jsonl, state/ticks.jsonl, state/changes.yaml, state/mistakes.jsonl.

## Constraints

- Python 3.12, stdlib plus PyYAML only. GitHub only through `gh api` as a subprocess; no
  urllib, http.client or third-party HTTP. Git only through `git` subprocesses, read-only.
- Never write outside this worktree; never edit `state/` (fixtures are copies under
  `tests/fixtures/metrics/`), never edit `posts/` or `prompts/`.
- Pattern to design against (plan decision 7): every value from a ledger, YAML, git or the API
  is untrusted; parsing and conversion degrade to counted diagnostics, never raise; what
  `compute` emits, `render_document` accepts, proved by tests running both together.
- Tick the plan's checklist as you go. Commit per checklist item with clear messages.
- No emojis, no em dashes anywhere, including fixture README and HTML.

## Definition of done

All of these, pasted into your final message with their output:

1. `uv run --with pytest pytest -q` from the worktree root: ends in `N passed` with no
   failures, N at least 40, and the product tests under `product/` are not collected (pytest.ini).
2. `bin/metrics`: prints `metrics: N indicators, U unavailable, S skipped`, writes
   `site/data/metrics.json`. Then `bin/metrics --json - | head -c 300`.
3. `bin/metrics --json - > /tmp/a.json && bin/metrics --json - > /tmp/b.json && cmp /tmp/a.json /tmp/b.json && echo identical`.
4. `bin/blog build`: prints `built N posts into site/`; then
   `rg -c "<h2>" site/metrics/index.html` is at least 10.
5. `rg -n "urllib|http\.client|requests" lab_metrics tests bin/metrics` prints nothing.
6. `bin/lint`: `lint ok`.
7. `git status --short` is empty after your last commit, and `git log --oneline main..HEAD`.

Final message under 40 lines: files changed, the seven outputs above, departures from the plan.
