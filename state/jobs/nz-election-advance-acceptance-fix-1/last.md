Committed `65fbef1`; not pushed.

Updated `advance_acceptance.py` to exclude inline-hidden text and descendants. Hidden count sentences return `ADVANCE_NOT_PUBLISHED`. Added both-route regressions in this branch’s tests; main-base tests untouched.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py product/nz_election/tests/test_harden*.py
518 passed in 358.04s (0:05:58)

bin/lint
lint ok (1311 text files)
```

Against the pre-fix PR head: `24 failed, 2 passed`, demonstrating the regressions.

Uncommitted `last.md` records commands, outputs, and why parser filtering covers this site’s markup. Open questions: none.