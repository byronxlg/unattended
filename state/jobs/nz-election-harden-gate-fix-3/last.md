Committed `d406b7f`. Not pushed.

- `check_workflow_history.py`: ignores guard evidence from the first `$'` line onward.
- `test_harden.py`: added four cases; existing tests unchanged.
- The reported regression fails on `191c461`.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py
162 passed in 0.25s

bin/lint
lint ok (996 text files)
```

`last.md` records the commit and command outputs; it remains uncommitted. Open questions: none.