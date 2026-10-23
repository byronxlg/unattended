Committed `eda2d3b`. Not pushed.

Changed only `snapshots/voting.json`, `pipeline/snapshots.py`, and new loader tests. Added EC-sourced dates, action links, terms and validation. No page code changed.

Verification:

```text
uv run --with pytest pytest -q product
935 passed in 337.15s (0:05:37)

bin/lint
lint ok (551 text files)
```

`git diff --stat main`: 3 files, 446 insertions, 2 deletions.

Uncommitted `last.md` lists all sources, deadlines and omissions. Open questions: none.