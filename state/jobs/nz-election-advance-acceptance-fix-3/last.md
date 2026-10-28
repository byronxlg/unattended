Committed `fb1df65`; not pushed.

Updated the matcher and branch-owned tests. Attached signs and decimal prefixes now produce `ADVANCE_RENDER_MISMATCH` on both routes.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py
315 passed in 410.15s (0:06:50)

bin/lint
lint ok (1311 text files)
```

Against `20b6792`: **10 failed, 4 passed**. Extra-digit and comma prefixes were already correctly rejected; the other cases demonstrate the bug.

Evidence recorded in uncommitted `last.md`. Main-base tests unchanged. Open questions: none.