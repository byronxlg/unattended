Committed `a5cd0fa`; not pushed.

Changed two test files, the fixture manifest and advance runbook. Original capture assertions remain exact; inventory checks derive from registered files.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_contracts.py
168 passed in 109.53s (0:01:49)

Third-capture throwaway copy, unchanged tests:
168 passed in 107.71s (0:01:47)

bin/lint
lint ok (1297 text files)

verify.py advance --require-year 2026
PASS advance
```

Scratch copy removed. Details and assertion rationale in uncommitted `last.md`. Open questions: none.