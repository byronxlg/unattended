Follow-up 3 on change/nz-election-night-design (head 12d16c0). Fix job: tests on origin/main are protected; do not edit
product/nz_election/tests/result_states_browser.py or test_result_states.py. The branch's own tests move with it.

Host run on 12d16c0 (supervisor, Chromium available):
  uv run --with pytest pytest -q -x product/nz_election/tests/test_night_deployed.py product/nz_election/tests/test_result_states.py \
    product/nz_election/tests/test_night_page.py product/nz_election/tests/test_design.py product/nz_election/tests/test_waterfall*.py \
    product/nz_election/tests/test_home*.py product/nz_election/tests/test_night*.py
  -> 1 failed, 101 passed: test_result_states.py::test_result_states_browser
     result_states_browser.py:75  assert search.bottom <= height * 2   (night/ at 390, in a settled/official result state)

This is main's contract that the electorate search sits within two phone screens on night/ at 390 (the first fresh review's
finding: majority cards push the search down). Fix-1 met it in the states you checked but not in the result states this
harness renders. Fix the layout so the search is within two screens at 390 in every state result_states_browser.py builds
(and keep its later assertions: map hidden on search, one row, the candidate name text it expects). Do not shrink type below
DESIGN.md tokens; collapse or reorder the night/ modules above the search per pages/night.md order.

Done when, with Chromium if your sandbox allows it (say so if not):
  uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night*.py \
    product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py product/nz_election/tests/test_waterfall*.py
  all pass; bin/lint ok. Commit, do not push, do not commit last.md or artifacts/.
