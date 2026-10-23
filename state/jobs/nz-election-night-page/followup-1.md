Follow-up 1 on change/nz-election-night-page (rebased by the supervisor onto main abdb71e; your commit is now ae48859, same tree on top of b523eda). Fetch nothing; work from HEAD.

Host result (Chromium runs here): both browser tests fail on your own assertion, not on setup.

`uv run --with pytest pytest -q product -k "test_xml_python_browser_parity or test_replay_makes_no_official_feed_request"`
-> 2 errors, both at product/nz_election/tests/night_browser.py:74
   `assert '2,851,211' in page.locator('#night-snapshot').inner_text()`

The snapshot text at that point (state final, speed 60, play clicked, clock.run_for(10000)):
  "Illustrative replay based on 2023 final results (illustrative-2023)
   1,425,602 valid party votes
   Party results: Illustrative replay based on 2023 final results, 300 seconds ..."
So after 10 s at x60 (600 illustrative seconds) the page shows the 300 s frame, half the total. Either the
replay advances one frame per tick regardless of speed, stops one frame short, or the speed select is not
read when play starts. Find the cause in web/night.mjs (not by changing the test's timing): at speed 60 the
replay must reach the end frame (2,851,211 votes, House 122) within the 10 s the test allows, and stop there.

You cannot launch Chromium in your sandbox, so prove it another way too: a Node test (node:test, no browser)
that drives the replay scheduler with a fake clock at speed 60 and asserts the final frame index after
10,000 ms, and fails on ae48859. Tests are this branch's own; they may move with the fix, but the
night_browser.py assertions stay as strong as they are (same numbers, same 10 s).

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py` passes except the two
Chromium fixtures (report them as before), the new Node test fails on ae48859 and passes on HEAD,
`uv run product/nz_election/pipeline/verify.py all` prints PASS all, `bin/lint` prints lint ok.
Commit on the branch; do not commit last.md or artifacts/; do not push. The supervisor reruns the browser
tests and the screenshot harness on the host.
