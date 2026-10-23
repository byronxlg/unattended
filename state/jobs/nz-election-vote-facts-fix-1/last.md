Committed `9731f12`. Not pushed.

Updated the loader’s offset validation and added six regression cases. No data or source changes.

```text
uv run --with pytest pytest -q product
941 passed in 355.24s (0:05:55)

bin/lint
lint ok (551 text files)
```

Temporarily removing the offset bounds caused both `+12:60` regression tests to fail. Restored the fix before verification.

Evidence recorded in uncommitted `last.md`. Open questions: none.