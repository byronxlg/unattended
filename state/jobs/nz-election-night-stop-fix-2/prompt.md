Follow-up 2 on PR #80 (night-stop), fix round, same branch change/nz-election-night-stop at 4c997ab.

CI run 40164335695 failed one test, reproduced on the host:

  product/nz_election/tests/test_result_states.py::test_result_states_browser
  result_states_browser.py:126 Page.wait_for_function timeout (dataset.mode never becomes the handover mode)

Cause: result_states_browser.py (on main at bd53141, from PR #79) installs the clock at 2026-11-27T11:00Z,
loads a pre-handover night/ page, flips the mocked night-live.json to the settled/official pack and runs the
clock 121 s, expecting the page to poll and hand over in place. Your fix-1 contract is zero requests at or
after the shared cutoff (2026-11-08T06:00Z), so the page never polls. The two contracts conflict; the bounded
stop wins. After the cutoff, settled and official states reach readers through the rebuilt, redeployed page
(the per-state builds in the same script, lines 36 to 55, already cover that), not through the live loop.

Authorized: the handover block of result_states_browser.py (the loop over handover_packs, about lines 100 to
135) moves with the contract. This is the only main test you may change. Invariants it must still enforce,
shape is yours:
1. In-place handover from a live poll is still proven where it is reachable: clock before the cutoff, a 503
   then the settled pack, the page switches mode, the result-status band goes, "Live preliminary results" is
   gone, the nav link behaves as today. Keep the existing assertions on that path, do not weaken them.
2. A pre-handover page loaded with the clock after the cutoff (the 27 Nov case) makes zero requests to
   night-live.json, raises no page errors, and shows whatever your ended state shows; assert that, plus that
   the official state is what the per-state build renders (existing per-state checks may already do this,
   then point at them in a comment rather than duplicating).
3. Nothing else under product/nz_election/tests on main at bd53141 changes. Your own branch tests move freely.

Done when, run on your side and named in your reply with the counts:
  uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night_stop_bootstrap.py product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_night_page.py
all pass (Chromium may be denied in your sandbox; say so, the host reruns them), and bin/lint ok.
Commit on the branch, do not push.
