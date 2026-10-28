# Follow-up 1: funding-rows guard (PR #133), fresh review findings

The fresh review requested changes. These files are this branch's own tests; they move freely. Touch nothing outside `product/nz_election/tests/funding_rows_browser.py` and `product/nz_election/tests/test_funding_rows.py`.

1. Readability, not just accessibility: at 360 and 390, for every party and every return, scroll the return into view and check the rendered text of each figure cell lies inside the viewport horizontally (left >= 0, right <= viewport width) and is not clipped by its cell (scrollWidth <= clientWidth, scrollHeight <= clientHeight), and that its computed opacity and colour are not transparent. Keep the existing accessible-name assertions.
2. Bounded lifetime: the subprocess in test_funding_rows.py gets a timeout (300 s) and on timeout kills the whole process group (start it in a new session), so no Chromium descendant survives. Start the local server cleanup before snapshot loading, so an exception in loading still stops the server.
3. Failure messages name the party, the return and the field, with the measured numbers.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_funding_rows.py` passes where Chromium launches (your sandbox may not; say so), `bin/lint` ok, one commit on the branch, no push. The check must still fail if the phone rules regain `min-width:620px` on the funding table: show that by a temporary local edit and revert it.
