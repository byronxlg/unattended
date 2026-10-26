# Follow-up 2: electorate-design (PR #98)

Second fresh review (state/jobs/review-nz-election-electorate-design-2/last.md) asks for two changes. Base of this branch: 6fda184 (main). Tests on main at 6fda184 are not edited; this branch's own tests (test_electorate_page_plan.py and any test added on change/nz-election-electorate-design) move with it.

1. Phone first screen. intent/nz-election/pages/electorate.md "Page order": at 390x844, above the fold are the electorate name, the candidate list (question 1) and the "is this mine" line (question 2: check your enrolled electorate at vote.nz, plus the boundary map link). Today the candidates are a single column of tall cards, so with seven (Nelson) or eight (Wellington North) candidates the enrolment line falls below the first screen. Keep candidates before the enrolment line; make the candidate presentation compact enough at phone width that both fit (your choice of shape, from DESIGN.md components and tokens; product/nz_election/DESIGN.md). 1280 may keep the richer layout. Do not drop any candidate data (name, party, list/electorate status) and do not go below DESIGN.md's reading floor or 44 px targets.
2. With an empty candidate list, the selected-seat map link (pipeline/home_graphics.py:314) targets `#candidates-title`, which is omitted. Give it a destination that exists on that page (or no link), whichever matches the absence rule.

Add browser checks (behaviour, not markup or class names): at 390x844 the bottom of the enrolment line's link is within the viewport for the electorate with the most candidates in the data, and every in-page map link target exists. Show each fails on 9488223 and passes on your commit.

Do not touch intent/ files. Commit in the worktree, do not push.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_electorate_page_plan.py product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py` passes (Chromium sandbox denials may be reported as such; the supervisor reruns them on the host) and `bin/lint` is ok. Report commands and output in last.md.
