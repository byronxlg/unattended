Committed `3228381`; not pushed.

Added vote/, NZ-midnight ordering, countdown timeline, official links, navigation and 80-route contracts.

Verification:
- `uv run --with pytest pytest -q product`: `1456 passed in 367.44s`
- `uv run product/nz_election/pipeline/verify.py all --site artifacts/vote/site`: `PASS all`
- `bin/lint`: `lint ok (576 text files)`

Incomplete: screenshot harness blocked by Chromium startup permission denial. Native Chrome access was also denied. Screenshots and visual question test remain unverified.

Details and expected screenshot filenames are in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-vote-page/last.md).