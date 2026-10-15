# Build: Fleet Audit increment 2, observer and replay

You are in the worktree `.worktrees/fleet-audit-2` on branch `change/fleet-audit-2`, cut from
`main` at 7666852 (increment 1 merged as PR #1). Read `AGENTS.md` first. Commit in this
worktree as you go; never push.

## Goal

Implement increment 2 of `intent/fleet-audit/plan.md` exactly as its "Increment 2: observer and
replay" section describes, plus the CI line the "Increment 1 CI step" section asks for in each
subsequent increment: bounded launchctl collection, structural launchctl parsing, override map,
snapshot capture and replay, the real and synthetic fixtures it lists, the named tests, the
observer acceptance stage, and verdicts containing only the rule-1 coverage guard. Nothing from
increments 3 to 5: no freshness, receipts interpretation, drift, or audit/scan verdict rules
beyond rule 1. If the plan's increment 2 names a CLI command, implement it; if it does not,
add none and say so in your final message.

## Read first, in this order

1. `intent/fleet-audit/plan.md`: Scope, Package and installation (file inventory), Shared
   records and boundaries, Validation and observation policy, Increment 2, Verification.
2. `intent/fleet-audit/spec.md`: Evidence record and collection, Offline replay and
   verification, Verdict decision order (rule 1 only), CLI and report contract, and every
   Supervisor decision (7, 9, 10, 11 and 12 bear on this increment). A decision overrides the
   body where they differ.
3. The increment 1 code you wrote: `product/fleet_audit/fleet_audit/{models,files,plists,
   registry,reports,acceptance}.py` and `tests/conftest.py`. Extend, do not rewrite.
4. Real evidence, read-only: `.worktrees/spike-fleet-audit/spike/` at commit 18c8e8c
   (`audit.json`, `records.json`, `snapshot.json`; `collect.py` and `launchctl_parse.py` are
   spike code, a reference only) and
   `intent/fleet-audit/evidence/print-disabled-gui501-2026-10-16.txt` (the real override text;
   keep all five disabled Apple labels, as the plan says).

## Constraints

- `subprocess` may be imported in `collect.py` only: fixed argv starting with `/bin/launchctl`,
  no shell, a timeout, a combined stdout and stderr byte limit, children reaped on timeout.
  No other module in the package imports `subprocess`; the AST test from increment 1 must be
  updated to allow exactly `collect.py`.
- Tests never run launchctl or any process: `tests/conftest.py` guard stays and still fails
  any `subprocess` event; the subprocess-bounds test uses fake process objects, as the plan
  says. Replay never reads an original host path, runs a command, or reads the live clock
  (the plan's trap test proves it).
- Fixtures: every real record labelled real with source (spike commit 18c8e8c or the evidence
  file path) and its capture time; synthetic variants labelled synthetic; `fixtures/README.md`
  updated. No environment values anywhere (keys only, decision 11). Keep fixtures small; the
  host has about 2.5 GiB free.
- Increment 1 behaviour stays: `registry --offline` still prints `OK registry`, the existing
  tests stay green and unchanged unless the plan requires a change (say which and why).
- Paths literal, `Value[T]` explicit, restricted YAML, bounded reads: as in increment 1.
- `acceptance.py` gains the `observer` stage; the offline guard must also fail any subprocess
  event and any non-fixture open during it.
- CI: in `.github/workflows/ci.yml`, append
  `uv run python -m fleet_audit.acceptance observer --offline` to the existing Fleet Audit step
  after the registry line. Change nothing else in that file.
- No emojis, no em dashes, anywhere. Comments say why. README: what the new commands and the
  snapshot workflow do, and what increment 2 does not do (no verdicts beyond coverage).
- Do not edit `state/`, `posts/`, `prompts/`, `intent/`, `bin/`, `runbook/` or `pytest.ini`.
  If the plan cannot be followed as written, say exactly where in your final message instead
  of departing silently.

## Definition of done

From `product/fleet_audit/`, all of these pass and you paste their actual output:

```
uv run python -m fleet_audit.acceptance registry --offline     (last line: OK registry)
uv run python -m fleet_audit.acceptance observer --offline     (last line: OK observer)
uv run --with pytest pytest -q                                 (zero failures; the plan's
                                                                increment 2 tests all present)
```

From the worktree root:

```
bin/lint                                                       (exit 0)
uv run --with pytest pytest -q                                 (no tests ran, exit 5)
rg -l subprocess product/fleet_audit/fleet_audit               (exactly collect.py)
```

Final message, under 40 lines: files changed, the command outputs above, the venv size
(`du -sh product/fleet_audit/.venv`), and any place the plan could not be followed.
