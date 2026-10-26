# night-design fix-5 (PR #94, branch change/nz-election-night-design, head 8eedc0c)

Host verification of 8eedc0c with Chromium (the sandbox cannot launch it) ran your fix-4 list:
`2 failed, 461 passed`. Both are real; fix the product, not the checks.

1. Main's contract, `product/nz_election/tests/test_night_deployed.py::test_browser_checks[rehearse]`
   fails `FAIL deployed-rehearse: source-links`. The check is `night_deployed.py:389-391` on main:
   inside `#night-snapshot`, `.source-actions a` must be exactly 4 links, all http(s), one with text
   `Official results`, and among them a `.json` and a `.csv` export. The same test passes on
   origin/main (a5b88b6, 3 passed on the host), so this branch's night markup dropped, renamed or moved
   one of those links. Restore that provenance (the four links where the deployed probe reads them).
   `night_deployed.py` and `test_night_deployed.py` are main's tests at a5b88b6: do not edit them.

2. The branch's own `night_design_browser.py:90`: after clicking `Find your electorate`,
   `search.bounding_box()['y']` is outside `[0, height)` (state and width not printed; the run is
   reduced_motion, viewports 390x844 and 1280x900). The jump link must land the reader with the
   search box on screen in every state you test, including with the map-key caveats that fix-4 made
   visible during search. Make the assertion message print state, width and the y value. This
   assertion may not be loosened; the branch's own tests may otherwise move with the change.

Definition of done (Chromium checks will fail in your sandbox with Permission denied; that is
expected, the supervisor reruns them on the host):

    uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night*.py \
      product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py product/nz_election/tests/test_waterfall*.py

non-browser cases all pass; `bin/lint` ok; `git merge-tree --write-tree origin/main HEAD` exits 0
(fetch first; merge origin/main in if it moved, never rebase). Commit, do not push, do not commit
last.md or artifacts/. In last.md, say what the jump target was and why the search left the screen.
