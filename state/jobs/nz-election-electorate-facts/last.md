Committed `f28be8e`. Not pushed.

- Added both snapshots, loader validation and offline tests.
- Corrected 60 candidate names and 2 affiliations.
- Boundaries: 71 electorates, no mismatches, 316,359 bytes.
- Existing tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product
935 passed in 353.70s (0:05:53)

bin/lint
lint ok (552 text files)
```

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-facts/last.md) contains sources, counts, sizes and omissions; uncommitted. Fifty optional ranks remain omitted from candidates but are recorded in reconciliation.

Open questions: none.