Fix-1 on PR #81 (fresh review request changes, one Important). Same worktree, same branch, commit, do not push.

Finding (product/nz_election/pipeline/verify.py:434-446): the required-family presence check runs before bundle validation only for an explicit `night --data`. When `night/index.json` is missing but still listed in the manifest, bundle/site validation fails first, so `all --require night,waterfall` reports CAMPAIGN_DATA and an explicit `waterfall` reports INVALID_INVENTORY instead of MISSING_NIGHT_FAMILY. Exit codes are already nonzero; the defect is the error code.

Invariant: whenever a family is required and its data is absent from the resolved data path (via --data or --site, any check that requires it, including `all`), the first failure reported is the missing-family code for that family (MISSING_NIGHT_FAMILY or the existing waterfall equivalent), regardless of whether the manifest still lists it. Choose the shape; keep campaign redaction and the optional-family SKIP lines as they are.

Tests: tests on main at the base sha are protected, do not edit them. Add regressions for the manifest-lists-but-file-missing case for `all --require night,waterfall` and explicit `waterfall` (and `night --site`), shown failing on 617dd80 and passing on HEAD.

Done when: `uv run --with pytest pytest -q product/nz_election/tests` for the verify and night_operation tests passes, `bin/lint` ok, and last.md names the commit, the commands and their output, and the new tests that fail on 617dd80.
