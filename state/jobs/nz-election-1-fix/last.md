Committed `3b234f6`; not pushed.

1. Parser validates single-quoted, double-quoted and unquoted attributes consistently.
2. Reference scanner distinguishes uses from definitions and resolves forward references without crossing poll boundaries.
3. Both allocators validate input shapes and raise exactly `INVALID_INPUT`; missing/null handling agrees.
4. JS maps preserve `__proto__` party IDs, verified through parity tests.

Added 38 regression cases. Existing tests and fixtures unchanged.

```text
$ uv run --with pytest pytest -q
........................................................................ [ 49%]
........................................................................ [ 98%]
..                                                                       [100%]
146 passed in 1.71s

$ bin/lint
lint ok (166 text files)

$ git status --short
```

Status output empty. No disagreements with the findings.