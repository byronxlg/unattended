Committed `8eac454` on top of `40258c2`. No push.

`vote_page.py` now uses plain-text source credits with retrieval dates. Items 2 and 3 and all tests remain unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py
3 failed, 138 passed in 37.88s

bin/lint
lint ok (1158 text files)
```

Only failures: sandbox-denied Chromium launches for `map`, `trend`, and `header`.

Updated `last.md`; it and `artifacts/` remain uncommitted.