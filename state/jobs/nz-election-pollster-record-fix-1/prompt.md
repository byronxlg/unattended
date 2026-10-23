Follow-up on PR #58 (fresh review request changes). Same worktree, same branch, commit on top of 49da422, do not push.

1. Herald-DigiPoll is in neither scores nor exclusions in product/nz_election/snapshots/pollster-record.json. The
   pinned 2017 capture 801707892 has its national poll of 4-14 December 2015 with fieldwork dates and party shares.
   Either score it under the same eligibility rule the other records use, or exclude it with a reason that the rule
   applies to every pollster-year alike (if you add an age cutoff, check it against YouGov's 2019 poll for 2020 and
   say which way that goes). Every eligible pollster in every pinned capture must end up in exactly one of scores or
   exclusions; add a completeness test that would have caught this omission.
2. pipeline/pollster_scorecard.py:115: month-only source dates are not checked against the documented month-end
   rule (Roy Morgan 2020 fieldwork_end 2020-09-29 still validates). Validate the bound against the source month and
   add a rejection test.

Tests on main at the base sha stay as they are; this branch's own tests and the snapshot may move. Done when
`uv run --with pytest pytest -q product` passes and `bin/lint` prints lint ok; report the counts, the record count
after the change, and do not commit last.md.
