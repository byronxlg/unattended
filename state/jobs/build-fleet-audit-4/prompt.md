# Build: Fleet Audit increment 4, three-way drift

You are in the worktree `.worktrees/fleet-audit-4` on branch `change/fleet-audit-4`, cut from
`main` at b786941 (increments 1 to 3 merged as PR #1, #2 and #3). Read `AGENTS.md`
first. Commit in this worktree as you go; never push.

## Goal

Implement increment 4 of `intent/fleet-audit/plan.md` exactly as its "Increment 4: three-way
drift" section describes: `drift.py` with `normalize_calendar` and `compare_job` (plan
"Shared records and boundaries", Drift boundary), the `Comparison` and `DriftFinding` records
filled on every audited job, loaded schedule parsing extended where the plan says, the report
carrying comparisons and findings with the exit-1 drift rule already in `reports.py`, rule 9
of `verdicts.py` now reading real comparison status (replace the increment 3 comment that says
drift is not yet computed), the real and synthetic fixtures the plan lists, every named test,
and the `drift` acceptance stage. Nothing from increment 5: no scan verdicts, no scan CLI, no
lab adoption.

## Read first, in this order

1. `intent/fleet-audit/plan.md`: Increment 4, Shared records and boundaries (Drift), Snapshot
   and fixture format, Verification.
2. `intent/fleet-audit/spec.md`: "Drift comparison" in full, "Verdict decision order" rule 9,
   "CLI and report contract" (exit 1 on any drift finding; drift retained alongside the
   verdict), and supervisor decisions 7 and 8. Decision 7: loaded KeepAlive and RunAtLoad are
   never inferred from disk; unsupported forms stay unknown with the raw form retained.
3. The increment 1 to 3 code: `product/fleet_audit/fleet_audit/*.py` and `tests/`. Extend, do
   not rewrite. `models.py` already has `comparisons` and `drift` on the job record and the
   schedule record (`interval_seconds`, `calendar`, `keep_alive`, `run_at_load`);
   `launchctl_parse.py` already parses `run interval` and calendar triggers; `registry.py`
   has `freeze_calendar` and `calendar_error`. `reports.audit_fleet` is where comparisons
   attach to each job before `evaluate`.
4. The real records to reuse: the tick `runatload`, nix skhd `keepalive`, PDW calendar and
   Apple talagent multi-calendar captures already under `product/fleet_audit/fixtures/`
   (observer and increment 2 fixtures); do not recapture, and do not invent loaded fields
   that those captures do not contain.

## Constraints

- `subprocess` stays in `collect.py` only. Tests never spawn a process; `tests/conftest.py`
  unchanged. Replay reads no original path, runs no command, reads no live clock; the drift
  acceptance runs under the same offline guard and refuses a `reviewed: false` expected.json.
- Findings only for known unequal values. An Unknown, Unsupported or Absent side gives status
  `unknown` and an uncertainty, never a finding; an absent service makes loaded pairs
  `not_applicable`; an omitted expectation produces no comparison at all.
- Program on disk is `Program` when present, otherwise `ProgramArguments[0]`; never invent
  argv from `Program`. Argv compares element for element, preserving spaces, empty strings,
  order and argv[0]; no shell splitting, no expansion. Paths compare as literal normalized
  strings, no realpath.
- Calendar canonical form: alternative order and map key order immaterial, identical
  alternatives deduplicated, Sunday 7 normalized to 0, omitted keys remain wildcards (a
  wildcard is not equal to a value). Compare only requested components; retain every observed
  component in evidence.
- Disk omissions of KeepAlive and RunAtLoad normalize to false; loaded tokens stay unknown
  unless the frozen supported representation proves the value; rule 8's disk fallback is
  never used by drift.
- Reason template exactly: `{field}: {left_source}={left_value} differs from
  {right_source}={right_value}`; kinds `wrong_program`, `wrong_arguments`,
  `wrong_working_directory`, `wrong_schedule`.
- Increments 1 to 3 behaviour stays: `registry`, `observer` and `verdicts --offline` still
  pass; their tests and fixtures unchanged unless the plan requires a change (say which and
  why). The increment 3 verdict fixtures have no drift, so their expected rule, verdict and
  exit must not change.
- Fixtures small, labelled real or synthetic with source and capture time or an explicit
  timestamp limitation; `fixtures/README.md` updated; no environment values.
- CI: in `.github/workflows/ci.yml`, append
  `uv run python -m fleet_audit.acceptance drift --offline` after the verdicts line. Change
  nothing else in that file.
- No emojis, no em dashes. Comments say why. README: what drift compares, the three pairs,
  what unknown means, and what increment 4 does not do (no scan).
- Do not edit `state/`, `posts/`, `prompts/`, `intent/`, `bin/`, `runbook/` or `pytest.ini`.
  If the plan cannot be followed as written, say exactly where in your final message instead
  of departing silently. When a verification command in this brief cannot be satisfied
  honestly, say so; never restructure code to make a check pass.

## Definition of done

From `product/fleet_audit/`, all of these pass and you paste their actual output:

```
uv run python -m fleet_audit.acceptance registry --offline     (last line: OK registry)
uv run python -m fleet_audit.acceptance observer --offline     (last line: OK observer)
uv run python -m fleet_audit.acceptance verdicts --offline     (last line: OK verdicts)
uv run python -m fleet_audit.acceptance drift --offline        (last line: OK drift)
uv run --with pytest pytest -q                                 (zero failures; every test the
                                                                plan's increment 4 names present)
```

From the worktree root:

```
bin/lint                                                       (exit 0)
uv run --with pytest pytest -q                                 (no tests ran, exit 5)
rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit   (exactly collect.py)
```

Final message, under 40 lines: files changed, the command outputs above, the venv size
(`du -sh product/fleet_audit/.venv`), and any place the plan could not be followed.
