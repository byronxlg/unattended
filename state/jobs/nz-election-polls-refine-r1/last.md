Committed `e9ca98d`; not pushed.

- `build.py`: TOP abbreviation in shared strips.
- `polls.css`: summary date inherits sentence typography.
- Added regression; existing tests unchanged.

Verification:
- TOP test: baseline fails; HEAD `1 passed`.
- `bin/lint`: `lint ok (859 text files)`.
- Full pytest: `1 failed, 2037 passed, 2 errors`. All three unsuccessful cases hit Chromium launch permission denial; zero skips.

Evidence in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-polls-refine/last.md). Host browser verification remains.