# Build: Fleet Audit increment 3, verdicts and freshness

You are in the worktree `.worktrees/fleet-audit-3` on branch `change/fleet-audit-3`, cut from
`main` at d0dd7de (increments 1 and 2 merged as PR #1 and PR #2). Read `AGENTS.md` first.
Commit in this worktree as you go; never push.

## Goal

Implement increment 3 of `intent/fleet-audit/plan.md` exactly as its "Increment 3: verdicts and
freshness" section describes, plus the CI line the "Increment 1 CI step" section asks for:
output observation, receipt tail reading and parsing, the complete fourteen-rule verdict table
for audit, the `audit` CLI command with the report exit calculation, receipt capture and
replay, the real and synthetic fixtures it lists, every named test, and the `verdicts`
acceptance stage. Nothing from increments 4 and 5: no drift comparison (rule 9 treats drift as
not yet computed, say so in a comment), no scan verdicts, no scan CLI, no lab adoption.

## Read first, in this order

1. `intent/fleet-audit/plan.md`: Increment 3, Shared records and boundaries (Output/receipts
   and Verdicts boundaries), Receipt algorithm and contract, Ordered verdict engine, Snapshot
   and fixture format (receipts/), Verification.
2. `intent/fleet-audit/spec.md`: Receipt and freshness semantics, Verdict decision order, CLI
   and report contract (audit exit precedence), and Supervisor decisions 1, 3, 4 and 5.
   Decision 4 replaces the body's completed/failed predicate for `ticks_jsonl`: `ran: false`
   with `error` null or beginning `skipped:` is completed; read it in full and implement it,
   not the body.
3. The increment 1 and 2 code: `product/fleet_audit/fleet_audit/*.py` and `tests/`. Extend,
   do not rewrite. `verdicts.py` already holds rule 1 as `Rule`/`Match`/`NoMatch`; add rules 2
   to 14 in that shape.
4. Real receipt lines: `state/ticks.jsonl` in this worktree at commit d0dd7de. Take the first
   `ran: true` line (ts 2026-10-15T08:38:30Z, rc "0"), the usage-limit skip line (ts
   2026-10-15T11:24:08Z) and the `ran: false, error: null` line (ts 2026-10-15T08:34:36Z).
   Record commit d0dd7de and each line's SHA-256 in the fixture provenance. Label them real
   content; any metadata or clock placed around them is synthetic with a real-content source.

## Constraints

- `subprocess` stays in `collect.py` only. Tests never spawn a process; `tests/conftest.py`
  unchanged. Replay reads no original path, runs no command, reads no live clock; the verdicts
  acceptance runs under the same offline guard and must also refuse a `reviewed: false`
  expected.json.
- Receipt reads: final 64 KiB only, one terminal newline removed, final physical line only,
  never search backward; before/after metadata compared; nonregular files rejected; no path
  found inside receipt contents is ever followed (decision 11 spirit: nothing from receipt
  text becomes a path or an environment value).
- Age boundaries exactly as the spec: A<=M fresh, M<A<=M+G within grace (cannot_determine),
  A>M+G late; equality is never late; future timestamp cannot_determine with no skew
  tolerance. M=1200, G=1800 for the lab job come from the runbook, not constants.
- Unknown values never satisfy a predicate; no collection error anywhere in a job permits
  healthy_idle; rule order is first match; the reason strings follow the spec's templates.
- Increments 1 and 2 behaviour stays: `registry --offline` and `observer --offline` still
  pass, their tests unchanged unless the plan requires a change (say which and why).
- Fixtures small, labelled real or synthetic with source and capture time or an explicit
  timestamp limitation; `fixtures/README.md` updated; no environment values.
- CI: in `.github/workflows/ci.yml`, append
  `uv run python -m fleet_audit.acceptance verdicts --offline` after the observer line.
  Change nothing else in that file.
- No emojis, no em dashes. Comments say why. README: the audit command, its exit codes, the
  receipt contract in one paragraph, and what increment 3 does not do (no drift, no scan).
- Do not edit `state/`, `posts/`, `prompts/`, `intent/`, `bin/`, `runbook/` or `pytest.ini`.
  If the plan cannot be followed as written, say exactly where in your final message instead
  of departing silently. When a verification command in this brief cannot be satisfied
  honestly, say so; never restructure code to make a grep pass.

## Definition of done

From `product/fleet_audit/`, all of these pass and you paste their actual output:

```
uv run python -m fleet_audit.acceptance registry --offline     (last line: OK registry)
uv run python -m fleet_audit.acceptance observer --offline     (last line: OK observer)
uv run python -m fleet_audit.acceptance verdicts --offline     (last line: OK verdicts)
uv run --with pytest pytest -q                                 (zero failures; every test the
                                                                plan's increment 3 names present)
```

From the worktree root:

```
bin/lint                                                       (exit 0)
uv run --with pytest pytest -q                                 (no tests ran, exit 5)
rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit   (exactly collect.py)
```

Final message, under 40 lines: files changed, the command outputs above, the venv size
(`du -sh product/fleet_audit/.venv`), and any place the plan could not be followed.
