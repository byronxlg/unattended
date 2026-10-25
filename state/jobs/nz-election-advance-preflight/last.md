Committed `e849bbf`. No page or production-capture changes.

Changed `advance.py`, `verify.py`, added `tools/advance_preflight.py`, `runbook/advance.md`, and expanded `test_advance.py` with four synthetic fixtures.

Shorter replacements are rejected with `SHORTER_ADVANCE_CAPTURE`. Preflight prints a review draft; acquisition time requires operator input.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance.py
97 passed in 18.43s

uv run product/nz_election/pipeline/verify.py advance
PASS advance

uv run product/nz_election/pipeline/verify.py advance --require-year 2026
FAIL advance: MISSING_ADVANCE_CAPTURE

bin/lint
lint ok (998 text files)
```

New shorter-replacement test fails against base `dc57e78`: `DID NOT RAISE ValueError`.

Full suite: `5 failed, 2611 passed, 2 errors`. Browser checks were blocked by Chromium’s macOS `MachPortRendezvous` permission denial.

Remaining gate: capture and review real 2026 data. Report saved in uncommitted `last.md`.