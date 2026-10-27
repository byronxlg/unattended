Committed `679e2fc`; not pushed.

Updated five CSS files, `DESIGN.md`, funding markup and three typography tests. Reading text now uses 16px+ tokens; funding totals are prominent with adjacent caveats.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests
17 failed, 2877 passed, 2 errors
```

Fixed six campaign-related failures. Recheck:

```text
uv run --with pytest pytest -q product/nz_election/tests --lf
11 failed, 4 passed, 2 errors
```

Remaining failures/errors all concern Chromium launch permissions. No tests skipped.

```text
bin/lint
lint ok (1110 text files)
```

Populated build passes. Screenshots and visual review remain blocked by the sandbox.

Details, tokens and declaration counts: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-type-scale/last.md), left uncommitted.