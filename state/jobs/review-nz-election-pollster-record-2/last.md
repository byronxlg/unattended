Verdict: **accept**. No Critical, Important, or Nit findings.

- Herald-DigiPoll’s 4-14 Dec 2015 poll from capture `801707892` is scored, with seven party shares and exact MAE. Regression coverage: `product/nz_election/tests/test_pollster_scorecard.py:295` and `:311`.
- Month-only dates now require the correct month-end and precision: `product/nz_election/pipeline/pollster_scorecard.py:118`. Nine regression cases at `product/nz_election/tests/test_pollster_scorecard.py:322` fail against the pre-fix validator.
- No existing test on `main` was modified or weakened.

Verification via `python3 -B -c` in-memory harness:
```text
PASS 209 regression cases in memory (two filesystem-specific tests excluded)
PASS month-end regression tests fail against pre-fix validator: 9/9
PASS pre-fix snapshot rejected: test_scorecard_pinned_capture_pollster_completeness
PASS pre-fix snapshot rejected: test_scorecard_herald_digipoll_has_no_age_exemption
```

Normal command `uv run --with pytest pytest -q product/nz_election/tests/test_pollster_scorecard.py` was blocked:
```text
Failed to initialize cache at /Users/byron/.cache/uv
Operation not permitted (os error 1)
```

Full pytest execution remains unverified under this read-only sandbox. No files changed.