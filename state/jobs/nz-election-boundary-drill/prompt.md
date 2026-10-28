# Build: isolated Actions boundary drill (readiness-5 increment 3)

Goal: prove in GitHub Actions, isolated (no production writes, no upstream access, no Pages deploy, no data-branch push), that the election-night time boundaries behave: startup eligibility of the night live loop, a queued run refused by the s197 freeze including the rollback path, a run in flight when the night stop cutoff (8 Nov 06:00Z) passes stops cleanly, every sunset in `pipeline/sunsets.py` (hourly, night, daily, social; schedule and manual) at one second before and at each cutoff, and the watchdog cutoff. Today the Actions stop proof begins already at the cutoff, and the freeze integration checks mostly read workflow text (night_rehearsal.py:121, test_night_operation.py:150). This change makes them executed checks with an injected clock.

Read first: AGENTS.md, product/nz_election/pipeline/sunsets.py, product/nz_election/pipeline/night_rehearsal.py, .github/workflows/nz-election-night-rehearsal.yml (its existing `import_only` input from #121 is the pattern to copy), product/nz_election/runbook/night.md (rehearsal section), state/jobs/research-nz-election-readiness-5/last.md item 3.

Build:
- A boundary harness (a module under product/nz_election/pipeline/ or tools/, your choice) that runs each boundary scenario against an injected clock and a temp state/data directory, and prints one `PASS <scenario>` or `FAIL <scenario> <code>` line per scenario and exits nonzero on any FAIL.
- A `boundary_only` boolean dispatch input on nz-election-night-rehearsal.yml that runs only the harness, with the same isolation guarantees as `import_only` (read the workflow to see how they are enforced, and keep them enforced, not just stated).
- Offline tests in a NEW file product/nz_election/tests/test_night_boundary.py. Each scenario has a test that fails if the boundary moves by one second or the guard is removed.
- Runbook: one short subsection in runbook/night.md naming the dispatch command (`gh workflow run nz-election-night-rehearsal.yml --ref main -f boundary_only=true`) and the PASS lines it must print.

Constraints:
- PR #122 (change/nz-election-night-recovery) is open and edits bin/night-watchdog, product/nz_election/pipeline/night_start.py, product/nz_election/tests/test_night_operation.py and runbook/night.md's watchdog section. Do not edit those three code files or test_night_operation.py; call them, do not change them. In night.md touch only the rehearsal section.
- Tests on main at your base sha are not edited. No change to sunset or cutoff values. Nothing weakens an existing check.
- No secrets, no network in tests.

Done when, in the worktree:
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_boundary.py product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_sunsets.py` passes.
- The harness run locally (the exact command you document) prints a PASS line for every scenario and exits 0.
- `bin/lint` prints `lint ok`.
- Commit in the worktree, do not push. last.md: commit sha, the command outputs above, the scenario list, and anything you could not prove offline.
