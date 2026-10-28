# nz-election-night-recovery fix-1

The fresh review of PR #122 requested changes. Both items confirmed by the supervisor. This is a fix round on your own branch: the tests this branch added move with it; tests on main at 1d1d9fa stay untouched.

1. Important, `product/nz_election/pipeline/night_start.py:71-91`: `--dispatch` without `--state` skips the six-attempt budget, and `--state` takes no lock, so a direct CLI call can dispatch alongside the watchdog or overwrite a reservation. Invariant: no dispatch of nz-election-night-live.yml happens without both the shared lock and a successful reservation in the shared ledger. Enforce it at this entry point (for example: `--dispatch` requires `--state`, and `reserve` holds the same lock the watchdog uses, or the CLI refuses dispatch outside the locked wrapper). You choose the shape; `bin/night-watchdog` must keep working.

2. Important, `product/nz_election/tests/test_night_operation.py:928`, `:988`, `:997`: the budget, invalid-ledger and post-reservation cutoff tests fail at 1d1d9fa only because `main()` there rejects the `state` keyword. Rewrite them through an interface both revisions support (the CLI via subprocess with a stubbed `gh` on PATH, or the watchdog wrapper), so that at 1d1d9fa they fail by dispatching too many times or too late, not by TypeError.

Add a test for item 1: a direct `--dispatch` without the lock/state does not call `gh workflow run`.

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_sunsets.py` passes.
- With `product/nz_election/pipeline/night_start.py` and `bin/night-watchdog` checked out from 1d1d9fa, the rewritten budget and cutoff tests fail on an assertion about dispatch count or timing (paste the failure lines in last.md), then restore.
- `bin/lint` prints lint ok.
Commit on the branch; do not push.
