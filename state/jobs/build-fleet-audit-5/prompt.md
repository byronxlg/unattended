# Build: Fleet Audit increment 5, scan, reports and lab adoption

You are in the worktree `.worktrees/fleet-audit-5` on branch `change/fleet-audit-5`, cut from
`main` (increments 1 to 4 merged as PR #1 to #4; the lab declaration is already committed at
`runbook/fleet/fleet.md`, see spec supervisor decision 13). Read `AGENTS.md` first. Commit in
this worktree as you go; never push.

## Goal

Implement increment 5 of `intent/fleet-audit/plan.md` exactly as its "Increment 5: scan,
reports and lab adoption" section describes: the `scan` command (non-Apple user LaunchAgents,
no runbook, the scan verdict vocabulary of decision 9), complete text and JSON reports per
"CLI and report contract", capture in scan mode, the ten synthetic fixtures the plan lists
plus the real rows it names, every named test, the `fleet` acceptance stage, and the package
README's final form. The lab declaration already exists: do not write, move or edit anything
under `runbook/`. The supervisor runs the live commands and publishes.

## Read first, in this order

1. `intent/fleet-audit/plan.md`: Increment 5, Shared records and boundaries, Snapshot and
   fixture format, Verification.
2. `intent/fleet-audit/spec.md`: "CLI and report contract" in full (text line format, JSON
   envelope, exit precedence 3, 1, 2, 0), the scan paragraphs (label filter, no-label rows,
   no invented freshness, loaded-disabled), supervisor decisions 1, 2, 6, 9, 11 and 13.
3. The increment 1 to 4 code: `product/fleet_audit/fleet_audit/*.py` and `tests/`. Extend,
   do not rewrite. `reports.py` already renders audit text and JSON and holds `exit_code`;
   `capture.py` already captures audit snapshots; `cli.py` has `declared` and `audit`.
4. The real evidence to reuse: the twelve real audit rows and three real receipt contents
   already under `product/fleet_audit/fixtures/` and `intent/fleet-audit/evidence/`; do not
   recapture and do not invent fields those captures lack.

## Constraints

- `subprocess` stays in `collect.py` only. Tests never spawn a process; `tests/conftest.py`
  unchanged. Replay reads no original path, runs no command, reads no live clock; the fleet
  acceptance runs under the same offline guard and refuses a `reviewed: false` expected.json.
- Scan: exclude valid labels beginning `com.apple.`; for unreadable or no-label plists exclude
  only filenames beginning `com.apple.`; never infer a label from a filename; never look up a
  service for a no-label row; stat plist-declared stdout/stderr paths once per path and never
  read them; no freshness verdict in scan (decision 1); loaded_disabled is its own verdict
  and exits 1 (decision 9); scan disabled exits 2 unless another definite finding forces 1.
- Reports: one stable escaped text line per job in the spec's format, then drift and
  uncertainty lines, then issues and the summary; JSON is the complete envelope with explicit
  nulls, unattempted observations present, stable job order, argv order preserved, UTC
  timestamps, observation refs, summary counts; environment variable keys may appear, values
  never, in text, JSON or snapshots. Unknown prints `unknown`, never zero.
- Exit precedence 3, 1, 2, 0 across jobs and report issues; incomplete or empty coverage
  never exits 0; validation failures exit 3 before any live collection.
- Increments 1 to 4 behaviour stays: `registry`, `observer`, `verdicts` and `drift --offline`
  still pass; their tests and fixtures unchanged unless the plan requires a change (say which
  and why).
- Fixtures small, labelled real or synthetic with source and capture time or an explicit
  timestamp limitation; `fixtures/README.md` updated; no environment values anywhere.
- CI: in `.github/workflows/ci.yml`, append
  `uv run python -m fleet_audit.acceptance fleet --offline` after the drift line. Change
  nothing else in that file.
- No emojis, no em dashes. Comments say why. README: what scan does and does not do, the
  three commands with one example each, the exit codes, the declaration directory rule
  (decision 13).
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
uv run python -m fleet_audit.acceptance fleet --offline        (last line: OK fleet)
uv run fleet-audit --help                                      (exit 0)
uv run --with pytest pytest -q                                 (zero failures; every test the
                                                                plan's increment 5 names present)
```

From the worktree root:

```
bin/lint                                                       (exit 0)
uv run --with pytest pytest -q                                 (no tests ran, exit 5)
rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit   (exactly collect.py)
```

Final message, under 40 lines: files changed, the command outputs above, the venv size
(`du -sh product/fleet_audit/.venv`), and any place the plan could not be followed.
