Committed `d7ccfc2`; not pushed. Added server fallback, clock-driven client handover, packaged summaries and regression tests.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_home*.py product/nz_election/tests/test_night*.py product/nz_election/tests/test_result_states*.py
11 failed, 365 passed, 2 errors

bin/lint
lint ok (1088 text files)

python3 product/nz_election/pipeline/verify.py all
PASS all
```

Not fully verified: three untouched assertions forbid home scripts; remaining failures/errors are Chromium launch failures. All four new browser cases and screenshots remain unverified.

Details and baseline failures: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-handover/last.md). Report and artifacts remain uncommitted.