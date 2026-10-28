# Build: home keeps its answer when an hourly update fails

Page plan: intent/nz-election/pages/home.md. Design: product/nz_election/DESIGN.md (tokens and components).

## Goal

On 28 Oct 20:09Z the hourly failed (polls parse_drift). The deployed home at 1280 and 390 then showed,
under the h1, only "The 29 Oct, 09:09 NZDT update failed; showing previous data from 29 Oct, 07:22 NZDT."
plus "Update details", and then funding. The answer to "who is ahead" (the poll average hero and seats)
was gone from above the fold. A failed update with retained data must render the same hero from the
retained data, with the failure as a small dated staleness note beside it (the stale-note style home
already uses after #126), never in place of the answer.

## Read first

- product/nz_election/pipeline/home.py and whatever decides the failed/overdue state (grep "update failed").
- intent/nz-election/pages/home.md (order: Q1 who is ahead above the fold).
- product/nz_election/DESIGN.md.
- Existing home tests: product/nz_election/tests/test_home*.py.

## Constraints

- Absent stays absent: if there is no retained poll average at all, the hero is omitted (no "not available" text).
- The note keeps its time, the previous-data time and the Update details link.
- Tests check data and visible text order (hero figures present and before the failure note when retained data
  exists; absent when none), not markup or class names. Existing tests on main move only if they pin the
  old order; say which in last.md.
- No changes to night/ files (an open PR touches night_page.py and result_states.py).

## Done when

- `uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_home*.py product/nz_election/tests/test_design.py` passes (state which browser cases the sandbox denied).
- New test fails on origin/main's home code and passes on HEAD.
- `bin/lint` prints `lint ok`.
- One commit on change/nz-election-home-failed, not pushed; last.md summarises.
