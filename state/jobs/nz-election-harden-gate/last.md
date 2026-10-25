Committed `d891756`. No push.

Changed:
- `check_workflow_history.py`: cron-aware coverage and active-window guards.
- `harden.py`, `verify.py`: shared optional checks; release acceptance uses `--require night,waterfall`.
- `test_harden.py`: added regressions; existing tests unchanged.
- `runbook/night.md`: documented release command.

Verification, all offline:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden.py
120 passed in 0.18s

bash evals/pages-verify-polls-only/check.sh
SKIP night: family absent (night/index.json)
SKIP waterfall: family absent (night/index.json)
PASS campaign
PASS all

bin/lint
lint ok (996 text files)
```

Additional verifier tests: `46 passed`.

Healthy annual-history and pre-night omission tests failed on base `dc57e78`, now pass. No workflow edits or protected-test changes. Report: `last.md`, uncommitted.

Open questions: none.