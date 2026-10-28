# Build: Actions rehearsal of settlement, import and rollback (nz-election-import-rehearsal)

Goal: the result-import chain has never run in Actions (`nz-election-result-import.yml` has zero runs). On
election night Claude operates it alone (Codex ends 7 Nov). Give it an isolated Actions rehearsal so the first
real use is not the first run: settlement capture prep from a pinned bundle, capture registration, import with
`state=settled`, then `state=official`, then `rollback=true`, each followed by a check of what the publication
target serves (manifest/data SHA and result state). Nothing in production moves: the target is an isolated
branch or local artifact, synthetic data is labelled synthetic and never registered as a real capture.

Read first: `AGENTS.md`; `.github/workflows/nz-election-result-import.yml`; `.github/workflows/nz-election-night-rehearsal.yml`
(the existing isolated-publication rehearsal, follow its pattern for the target and served-SHA checks);
`product/nz_election/tools/settlement_capture.py`; `product/nz_election/tests/test_result_import.py`
(`test_rehearsal_imports_pin_and_rollback`), `test_settlement_capture.py`, `test_result_states.py`;
`product/nz_election/runbook/night.md` (the import and rollback sections).

Constraints:
- Choose the shape: a new job in the night rehearsal workflow, or a `rehearse` input on the import workflow, or a
  small new workflow. It must be `workflow_dispatch` only, never scheduled, never write `data` or deploy Pages.
- Every production guard stays as it is (freeze, sunsets, leases); do not move a clock or a constant to simulate.
- The workflow history checker (`tools/check_workflow_history.py`) and `test_workflows.py` contracts move with the
  registered workflow set if you add a workflow; tests on main at the base sha otherwise stay untouched.
- Runbook: add one short section to `runbook/night.md` naming the dispatch command and the PASS lines to read.
- No secrets, no network other than the GitHub runner's own checkout.

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py product/nz_election/tests/test_settlement_capture.py product/nz_election/tests/test_result_states.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_night_rehearsal_contract.py`
  passes (report the counts), plus a new test that runs the rehearsal entry point locally against a disposable
  bare Git target and asserts settled, official and rollback each print a PASS line with the served SHA.
- `bin/lint` passes.
- Commit on this branch; do not push. last.md lists the dispatch command the supervisor runs after merge and the
  exact PASS lines expected in the run log.
