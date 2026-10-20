Committed `db83ff9`; not pushed.

Changed only `donations.json`, `donations.py`, `snapshots.py`, and new loader tests. Snapshot contains 94 returns with exact amounts, provenance, and correction links.

Verification:

```text
uv run --with pytest pytest -q product
1325 passed in 343.35s (0:05:43)

bin/lint
lint ok (560 text files)
```

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-donations-facts/last.md) contains party counts/totals, every skipped URL, and the scoped diff.

Capture remains partial: 33 image-only PDFs, 19 fetch failures, and raw-byte archival unresolved.