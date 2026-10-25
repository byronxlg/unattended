Committed `191c461`. Not pushed.

- `check_workflow_history.py`: preserves quoted newlines, comment boundaries, and backslash continuations.
- `test_harden.py`: added 14 cases; existing tests unchanged.
- All three requested regressions failed on `9c5c5fc`. Evidence recorded in uncommitted `last.md`.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden.py
158 passed in 0.23s

bin/lint
lint ok (996 text files)
```

Checks ran offline. Open questions: none.