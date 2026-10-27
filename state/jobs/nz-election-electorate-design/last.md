Committed `1a23dc1`: shared hex locators, candidate race cards, licensed portraits, thicker result bars, and enrolment/Policy.nz actions.

Verification:

- `uv run --with pytest pytest -q product/nz_election`: **2903 passed, 14 failed, 2 errors**. All failures/errors are Chromium sandbox launch denials.
- `bin/lint`: **lint ok (1138 text files)**.

Acceptance remains incomplete: screenshots, mobile fold/overflow, and visual review are blocked. General seats use “General electorate” because no sourced region mapping exists.

Files, migrated checks, and pending screenshots are documented in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-design/last.md). Nothing pushed.