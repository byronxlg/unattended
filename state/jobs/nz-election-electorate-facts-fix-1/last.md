Committed `99f69dc`. Not pushed.

Updated `snapshots.py` and reconciliation tests: validates both correction values by field. Data, sources and base tests unchanged.

```text
uv run --with pytest pytest -q product
1003 passed in 338.67s (0:05:38)

bin/lint
lint ok (552 text files)
```

Removing only the new validation in memory caused all 62 rejection tests to fail.

Results recorded in uncommitted `last.md`. Open questions: none.