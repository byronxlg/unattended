# Follow-up 3 on PR #82 (post-schedules): one contract conflict in main's browser test

Host verification of 8e52f53: 272 passed, lint ok, one failure that your sandbox could not run (no Chromium):

```
product/nz_election/tests/result_states_browser.py:133
assert 'official results due 27 November' in page.locator('#night-result-status').inner_text()
```

For the non-settled states that loop installs the clock at `datetime(2026, 11, 27, 11, tzinfo=timezone.utc)`, which is 28 Nov 00:00 NZDT, past the date, with no official provenance yet (the feed answers 503 until handover). Follow-up 2 said the night "due 27 November" pins on main were all pre-27-Nov states; that was a supervisor error for this one. The pin contradicts the invariant you implemented, so it moves.

Authorized: in `result_states_browser.py`, only the assertion at line 133 (and nothing else in that file) may change: for the settled state (instant before CLOSE) it keeps asserting 'official results due 27 November'; for the post-date instant it asserts the neutral wording your predicate produces and that 'due 27 November' is absent. Every other test on main at eb9dcf7 stays as it is. No product code change unless the neutral text is not what the page shows, in which case fix the product, not the test.

Definition of done (report outputs in last.md, do not commit last.md):
- `uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_night_page.py` passes where Chromium is available; if your sandbox cannot launch Chromium, say so and run `python -m py_compile product/nz_election/tests/result_states_browser.py` plus the non-browser tests. The supervisor runs the browser tests on the host.
- `bin/lint` ok. Commit on this branch, do not push.
