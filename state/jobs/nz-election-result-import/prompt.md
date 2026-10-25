# Build: result-import workflow (week-after increment 2, readiness audit item 2)

Worktree `.worktrees/nz-election-result-import`, branch `change/nz-election-result-import` from origin/main. Commit
there, never push. No page or template changes: this is a pipeline and workflow change.

## Goal

The settled and official result transitions (`product/nz_election/pipeline/result_states.py`) only prepare local
artifacts; no workflow runs them, and `product/nz_election/runbook/night.md:392` refers to a "separate official import
workflow" that does not exist. After 7 November Claude operates alone and must be able to publish the settled and then
the official state from GitHub Actions, traceably, with one dispatch each. Build that path.

## Read first

- `product/nz_election/pipeline/result_states.py` (transition, validate, main)
- `.github/workflows/nz-election-night-live.yml` and `nz-election-daily.yml`: how a job pins inputs, verifies, uses the
  leased publisher for one family and triggers the Pages deploy. Reuse their publisher and lease; do not write a new one.
- `product/nz_election/runbook/night.md` around 230-400 (rehearsal, settled/official sections)
- `product/nz_election/pipeline/verify.py` (night, waterfall), `product/nz_election/pipeline/sunsets.py`
- `intent/nz-election/plan-week-after.md`
- the s197 freeze guard used by the existing publication workflows

## Requirements

1. New `.github/workflows/nz-election-result-import.yml`, `workflow_dispatch` only (no schedule). Inputs: `state`
   (settled or official), `capture` (manifest-checked fixture path of the reviewed human capture, committed on main),
   `data_sha` (the data-branch commit to transition from). The job checks out the data branch at exactly `data_sha`
   and fails if it is not reachable from the data branch head; runs `result_states.py` with
   `--run-url` set to the producing run URL and `--now` from the job clock; runs `verify.py night` and
   `verify.py waterfall` on the output; publishes only the night family through the existing leased publisher; and
   triggers the Pages deploy the way the other publication workflows do. The summary names the input data sha, the
   capture path and its sha256, the published data sha, and the PASS lines.
2. Refusals, each a named code in the log and nonzero exit, before anything is published: capture path not in the
   manifest or not a real capture (synthetic fixtures under the test or rehearsal paths are rejected in this workflow);
   state official with a source that `result_states.validate` rejects (wrong source, date before the official date,
   reference mismatch); data_sha not on the data branch; the freeze window active; verify not PASS. Reuse existing
   codes where they exist.
3. Rollback: a documented, tested way to republish the night family from the pre-import data sha (a `rollback` input
   or a documented rerun of the publisher with `data_sha`), in the runbook with the exact `gh workflow run` commands.
4. Runbook: replace the "separate official import workflow" text with the real workflow, the exact dispatch commands for
   settled and official, what to check after (verify lines, live night/ state, Pages run), and the rollback.
5. Tests (pytest, injected transport or local git fixtures, no network): settled and official fixture rehearsal
   through the workflow's script path ending in PASS; each refusal in item 2 with its code; data_sha pinning; that the
   workflow has no `schedule:` and publishes only the night family. Workflow discovery and contract tests that
   enumerate the workflow set (for example `test_workflow_discovery`, `test_workflows`, the harden history check if it
   lists workflows) move with the registered set; nothing weaker. Do not edit unrelated tests.

## Constraints

- No secrets in the tree, no new paid service, no infrastructure outside the workflow file.
- Keep logic in Python under `product/nz_election/` so it is testable; the workflow calls it.
- Synthetic captures never reach production.

## Definition of done

```
uv run --with pytest pytest -q product/nz_election/tests/test_result_states*.py product/nz_election/tests/test_workflow*.py product/nz_election/tests/test_night_operation.py <your new test file>
```
all pass; `bin/lint` prints `lint ok`; `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/nz-election-result-import.yml'))"`
exits 0. Report the commands and outputs, the new refusal codes, and open questions in `last.md` (do not commit it).
