Committed `8ec1200`; not pushed.

- Linked **71 of 71 electorates** to HTTP-200, name-confirmed destinations.
- Corrected seven party provenance URLs.
- Updated rendering, strict validation and regression tests.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/
5 failed, 2626 passed, 2 errors in 747.41s

bin/lint
lint ok (1077 text files)
```

All seven failures/errors are Chromium sandbox launch failures. New tests pass and the regression fails against `origin/main`.

**Incomplete:** screenshots and visual placement verification are blocked by the same sandbox restriction. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-policy-links/last.md). Report and artifacts remain uncommitted.