Follow-up 1 on d7ccfc2 (build round, same branch). Supervisor host run: test_home_handover.py 12 passed with host
Chromium; home_handover_browser absent PASS; screenshots looked at.

1. Contract conflict (supervisor brief error): the handover needs a client module, and three tests on main at the
   base sha forbid any home script: test_home.py::test_home_module_order (line 49, '<script' not in html) and
   test_design.py::test_real_first_view_budget (no .mjs on home), which test_poll_budget_rejects_oversized_dependency
   calls. These may move, and only this far: home may load exactly one module, web/home-live.mjs, with a byte cap
   (under 2,048 bytes transferred, asserted); every other .mjs and the explorer assets (allocator.mjs,
   data/averages.json, data/seats.json) stay forbidden on home; the oversized-dependency cases still fail for the
   damaged polls budget they were written for. Name each moved line in last.md.
2. Defect at 06:01 NZDT 7 Nov (artifacts/home-0601-390.png): above "Who is winning now?" the line still reads
   "Enrolment closed on 25 October; advance voting from 26 October; election day 7 November." After polling close it
   must not speak of voting as upcoming: replace it with past-tense copy (voting closed at 7pm on 7 November) or drop
   it, server render and client alike; a test at the 06:01 clock that fails on d7ccfc2.

Done: `uv run --with pytest pytest -q product/nz_election/tests/test_home*.py product/nz_election/tests/test_design.py`
passes except browser launches the sandbox blocks (list them); bin/lint ok; one new commit; do not push; do not
commit last.md or artifacts/.
