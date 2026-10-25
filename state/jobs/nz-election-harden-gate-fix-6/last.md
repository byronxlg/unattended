Committed `2c5342f`. Not pushed.

Folded YAML scalars now provide no guard evidence. Both regressions fail on `e04e72b`. All six real workflow classifications remain unchanged; protected tests are untouched.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py
262 passed in 1.14s

bin/lint
lint ok (996 text files)
```

Commands, outputs, and the branch-test adjustment are recorded in uncommitted `last.md`.