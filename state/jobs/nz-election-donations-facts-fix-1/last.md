Committed `b065f31`; not pushed.

All 146 index returns included; zero skips. Added party IDs, conservative PDF-check flags, count validation, and tests. Preserved the Alajamber date conflict explicitly.

```text
uv run --with pytest pytest -q product
1434 passed in 340.32s (0:05:40)

bin/lint
lint ok (563 text files)
```

Diff against `main` contains only snapshots, loaders, and tests. Existing tests remain untouched.

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-donations-facts/last.md) contains party totals, unchecked-document counts, verification output, and the unresolved date question. It remains uncommitted.