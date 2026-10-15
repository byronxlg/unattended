# Build: Fleet Audit increment 1, registry and plist join

You are in the worktree `.worktrees/fleet-audit-1` on branch `change/fleet-audit-1`. Read
`AGENTS.md` first. Commit in this worktree as you go; never push.

## Goal

Implement increment 1 of `intent/fleet-audit/plan.md` exactly as the plan's "Increment 1:
registry and plist join" and "Increment 1 CI step" sections describe: the package skeleton
under `product/fleet_audit/`, the runbook registry (schema version 1, strict validation), the
plist join, a declared-only CLI, the registry acceptance stage, fixtures, and tests. Nothing from
increments 2 to 5: no launchctl code, no subprocess module import anywhere in the package, no
verdict rules beyond what `declared` needs.

## Read first, in this order

1. `intent/fleet-audit/plan.md`: sections Scope, Package and installation, Shared records and
   boundaries, Validation and observation policy, Increment 1, Increment 1 CI step,
   Verification. The file inventory table names every file; create only those increment 1 needs.
2. `intent/fleet-audit/spec.md`: Runbook schema version 1 (the table is the contract; messages
   are literal suffixes), CLI and report contract (the `declared` command and exit codes), and
   Supervisor decisions 2, 8, 11, 12. Where a decision differs from the body, the decision wins.
3. `intent/fleet-audit/intent.md` for the why.
4. `.worktrees/spike-fleet-audit/spike/audit.json` for the real plist projections (read-only;
   that worktree is at commit 18c8e8c; record that in `product/fleet_audit/fixtures/README.md`).
   `intent/fleet-audit/evidence/` holds the real print-disabled output; not needed this increment.

## Constraints

- Python 3.12 (`requires-python = "==3.12.*"`), runtime dependency exactly `PyYAML==6.0.2`,
  build backend `setuptools.build_meta` pinned as the plan says, commit `uv.lock`. Keep the
  install small; the host has about 2.5 GiB free. Report `du -sh product/fleet_audit/.venv` in
  your final message (the plan asks for the measured footprint).
- Paths are literal strings: no tilde or environment expansion, no realpath, no existence checks
  of executables or working directories. Only plist files are opened, through the bounded
  regular-file reader (1 MiB cap).
- `Value[T]` variants (`Known`, `Absent`, `Unknown`, `Unsupported`) never support implicit
  truth testing; `__bool__` raises.
- Frontmatter uses a restricted PyYAML loader as the plan's validation policy says: reject
  aliases, tags, duplicate keys, nulls, implicit coercion; `reviewed` must be a quoted string.
- Fixtures: real projections labelled real with their source; anything reconstructed (XML or
  binary plist bytes) labelled synthetic in `fixtures/README.md`. Never copy environment values
  into fixtures; the tick plist's `EnvironmentVariables` keeps keys only (decision 11).
- `tests/conftest.py` must guard against live access: any `subprocess` use or any open of a
  path under `/Users/byron/Library` during tests is a failure.
- CI: edit `.github/workflows/ci.yml` (you are allowed to, for this file only) by adding a step
  after Tests that runs, with `working-directory: product/fleet_audit`, `uv sync --locked`,
  `uv run python -m fleet_audit.acceptance registry --offline`, and
  `uv run --with pytest pytest -q`. Do not change the Lint step. Do not wrap the new step in a
  file-exists condition.
- No emojis, no em dashes, anywhere. Comments say why. Keep the README factual: what the
  commands do and what increment 1 does not do (no live observation yet).
- Do not edit `state/`, `posts/`, `prompts/`, `intent/`, `bin/` or `runbook/`. If the plan
  cannot be followed as written, say exactly where in your final message instead of departing
  silently.

## Definition of done

From `product/fleet_audit/`, all three commands pass and you paste their actual output:

```
uv run python -m fleet_audit.acceptance registry --offline
```
prints exactly `OK registry` as its last line and exits 0.

```
uv run --with pytest pytest -q
```
runs the nine increment 1 tests named in the plan (the schema rejection matrix may be one
parameterized test) with zero failures.

From the worktree root:

```
bin/lint
```
exits 0.

Also show `uv run fleet-audit declared <fixture runbook dir>` on the valid fixture (exit 0,
one `declared` line per job) and on the schema-errors fixture (exit 3, errors on stderr), and
`uv run fleet-audit --help` (exit 0). The console script and `python -m fleet_audit.acceptance`
must both resolve from the installed package.

Final message, under 40 lines: files changed, the command outputs above, the venv size, and
any place the plan could not be followed.
