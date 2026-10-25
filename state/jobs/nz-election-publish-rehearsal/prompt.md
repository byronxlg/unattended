# Build: make publication and recovery rehearsable before polls close (readiness-3 increment 2)

## Goal
Election night's server-side loop (`product/nz_election/pipeline/night_live.py`, the night-live workflow) has never run
its publication path end to end: the current Actions rehearsal deliberately bypasses publication, deployment recovery and
successor chaining (night_live.py around :250), and the deployed faults start from a good package and only test browser
retention (tests/night_deployed.py around :381). Add an isolated rehearsal target that exercises the production
orchestration without publishing demo results into production data or the production Pages site.
Audit: `state/jobs/research-nz-election-readiness-3/last.md`, item 2.

## Read first
`AGENTS.md`, `REVIEW.md`, `pipeline/night_live.py`, `pipeline/publish.py`, `.github/workflows/` (night-live and pages),
`bin/night-watchdog`, `product/nz_election/runbook/night.md`, `tests/test_night_operation.py`, `tests/test_workflows.py`,
the freeze rules in `intent/nz-election/plan-m3.md` (increment 5).

## Constraints
- Isolation: the rehearsal writes to its own ref (for example a `rehearsal-data` branch or a run artifact) and never to
  the production data branch or the production Pages deployment; a test proves the production ref is untouched.
- Exercise, in order, with an injected or demo feed: first-feed failure (no publication, retry), a complete cycle
  published, a failed deployment and its recovery, the successor run chained before the job timeout, and the bounded stop.
- The same freeze guard and 19:00 NZDT start guard as production apply to the production path; the rehearsal target is
  allowed before 19:00 only because it cannot reach production. Do not loosen either guard; queued-publication and
  rollback tests in test_night_operation.py (around :139) keep passing unchanged.
- Workflow is dispatch-only (no new cron). No secrets added.
- No network in pytest. Main's tests at origin/main move only where a contract named here moves; say which in last.md.

## Definition of done
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py`
  passes; new tests fail against origin/main's night_live.py (show it).
- `bin/lint` ok; the workflow YAML parses (`python3 -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' <file>`).
- runbook/night.md gains the rehearsal dispatch command and what to verify (served code SHA, data SHA, production ref
  unchanged). The supervisor will dispatch it in Actions after merge as the proof.
- Commit in the worktree; do not push. last.md: files, commands with output, what you could not run.
