# Build: repeatable Harden gate (M3 Wed 4 Nov acceptance)

No page change: tooling and runbook only.

## Goal

The 4 Nov Harden milestone (`intent/nz-election/schedule.md`) needs: all evals green, `verify.py all`
PASS with explicit family lines, every scheduled workflow green three days running, the s197 social
freeze tested. Each piece exists but nothing runs them together. Build one command that does, so the
supervisor can run it daily and record the result.

1. `bin/nz-election-harden --data <bundle> --site <site>`: runs every `evals/*/check.sh` (discover
   them, do not hardcode the list; a network-dependent eval such as `pages-home-bytes-live` may be
   skipped only with `--offline`, printed as SKIP with the reason, and SKIP makes the overall result
   not PASS), then `verify.py all --data --site` and requires the explicit lines `PASS night`,
   `PASS waterfall`, `PASS campaign` (and every other family line the verifier prints) before
   `PASS all`, then the focused freeze tests (`test_social.py`, `test_social_fix_round1.py`,
   `test_night_operation.py`). Last line `PASS harden` or `FAIL harden: <first failing step>`.
2. `product/nz_election/tools/check_workflow_history.py --days 3`: reads `gh run list` JSON (inject
   the runner so tests need no network) for the scheduled workflows (hourly, daily, social daily;
   discover names from `.github/workflows/`), and reports for each NZ calendar day in the window
   whether the workflow had at least one successful run and how many failures, flagging days where a
   cron did not fire and a by-hand dispatch covered it (event `workflow_dispatch`). PASS only when
   each workflow has a success on each of the last N complete days. Include it in the harden command
   behind `--history` (network, off by default in tests).
3. Runbook: a "Harden gate" section in `runbook/nz-election.md` with both commands and how to read
   them.

## Read first

`intent/nz-election/schedule.md`, `intent/nz-election/plan-m3.md` (common verification paragraph),
`product/nz_election/pipeline/verify.py` (this branch includes the new `campaign` check),
`evals/*/check.sh` and their READMEs, `.github/workflows/`.

## Constraints

- This branch stacks on change/nz-election-campaign-verify (PR #75, under review). Do not modify
  anything that PR changed.
- Do not edit `product/nz_election/runbook/night.md`, `product/nz_election/tests/night_*`, pages,
  templates or web files; another job owns them. Do not edit `.github/workflows/` (CI wiring is a
  later decision; note in last.md what you would add).
- No secrets. Tests for both tools with injected subprocess/gh runners, in
  `product/nz_election/tests/test_harden.py`; existing tests untouched.

## Definition of done

- `uv run --with pytest pytest -q product/nz_election/tests/test_harden.py` passes;
  `uv run --with pytest pytest -q` passes; `bin/lint` prints ok.
- `bin/nz-election-harden --offline --data <fixture bundle> --site <fixture site>` run, last line
  pasted (FAIL is acceptable if a real check fails; name it and do not weaken it).
- Commit on the branch; last.md lists files, commands and last lines.
