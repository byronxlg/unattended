# nz-election-m3-live fix-3 (PR #65, host browser run on 8da4d3a)

Host run on 8da4d3a (Chromium starts on the host):
- `uv run --with pytest pytest -q -x`: 1144 passed, then ERROR test_night_page.py::test_xml_python_browser_parity
  (fixture runs night_browser.py).
- `uv run product/nz_election/tests/night_browser.py <out>` standalone: same failure, reproduced:
  `night_live_browser.py:115 assert resume['calls'] == [dict(at=resume['at'], hidden=False)]` AssertionError.
- On 727561e the same suite passed on the host at 08:05Z (1938 passed, night_browser via the parity test), so fix-2
  changed what the page fetches on resume (likely the freshness publication or recovery changed night-live.json,
  its URL, or the polling schedule so a second or zero fetch now happens on resume).

Fix: find which side moved. The contract stays: no fetch while hidden, exactly one fetch on resume. If the page now
fetches twice (e.g. freshness and results), fix the page; if fix-2 changed the payload so the fake server in the
harness serves something the page treats differently, align the harness fixture with the real published shape
without loosening the assertion. Make the assertion print `resume['calls']` on failure so the next host run shows
it. Both fix-2 regressions must keep passing. Tests on main at the PR base may not be weakened.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_night_operation.py`
  passes (browser parts may error in your sandbox: say so).
- Explain in last.md what the resume calls were and why, from reading the code.
- `bin/lint` ok. Commit on change/nz-election-m3-live; do not commit last.md or artifacts/.
