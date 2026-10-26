Committed `932d108`; not pushed.

Missing, null or empty source URLs now omit the link while preserving the closed message. Added one parametrized regression test; it fails on prior head `06a1a8b`.

```text
uv run --with pytest pytest -q product/nz_election/tests -k vote
205 passed, 2824 deselected in 6.25s

bin/lint
lint ok (1145 text files)
```

Commit and test outputs recorded in `last.md`, left uncommitted.