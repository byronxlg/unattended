Committed `49da422`; not pushed.

Added the sourced snapshot, pinned captures, exact-arithmetic loader and tests. Includes 19 scored pollster-years and documented exclusions.

```text
$ uv run --with pytest pytest -q product
1636 passed in 358.58s (0:05:58)

$ bin/lint
lint ok (579 text files)
```

Diff against `main`: only snapshots, loader and tests. Existing tests untouched.

Audit: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-pollster-record/last.md), intentionally uncommitted. Publication bounds and month-only fieldwork limits documented. No open questions.