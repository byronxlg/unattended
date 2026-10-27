Committed `50c1736`. No push.

Credits now include every drawn dated record, regardless of URL. Added three regression tests; existing tests untouched.

Verification:
```text
New regressions on 8eac454: 3 failed
New regressions after fix: 3 passed

uv run --with pytest pytest -q product/nz_election/tests -k vote
208 passed, 2828 deselected in 7.37s

bin/lint
lint ok (1159 text files)
```

No sandbox failures. Updated `last.md`; it and `artifacts/` remain uncommitted.