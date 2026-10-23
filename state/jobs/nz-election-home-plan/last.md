Committed `cf770ea`; not pushed. Rebuilt home order, seat strip, combined polling charts, electorate picker and timed night handover. Markets remains on Methods.

Verification:
- `uv run --with pytest pytest -q product --tb=short`: `1921 passed, 2 failed, 2 errors`. Fixed the markup failure; focused rerun: `45 passed`.
- Remaining three browser cases fail because Chromium cannot start in the sandbox.
- `uv run product/nz_election/pipeline/verify.py all --site artifacts/nz-election/before`: `PASS all`.
- `bin/lint`: `lint ok (643 text files)`.

Screenshots and the visual question test remain blocked. The enrolment flip says “Enrolment closed”, matching the [EC guidance](https://vote.nz/enrolling/enrol-or-update/enrol-or-update-online).

Changes, test migrations and blockers are recorded in uncommitted [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-plan/last.md).