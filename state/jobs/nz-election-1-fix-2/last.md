Committed `af8f50b`; not pushed.

- Python normalizes finite integral floats before exact arithmetic; numeric validation agrees with JS.
- JS sorts party IDs by code point, matching Python.
- Parser recognises attribute names case-insensitively.
- Added 25 regression cases; existing tests and fixtures unchanged.

```text
$ uv run --with pytest pytest -q
........................................................................ [ 42%]
........................................................................ [ 84%]
...........................                                              [100%]
171 passed in 2.50s

$ bin/lint
lint ok (167 text files)

$ git status --short
```

Status output empty. No disagreements.