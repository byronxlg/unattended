# Follow-up 1: your own browser regression fails on the host

Host Chromium (not sandboxed) ran your required command on 3db3adc:

```
uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_design.py
1 failed, 140 passed
FAILED test_night_page.py::test_empty_night_first_capture_and_cutoff
playwright TimeoutError: Locator.fill: Timeout 30000ms exceeded. waiting for get_by_role("textbox")
```

`night_empty_browser.py` (this branch's own harness) waits for an electorate search textbox that never appears.
Decide which side is wrong: if the empty shell should offer electorate search once the first capture arrives
(pages/night.md question 3), the page is wrong and must render or reveal it; if the search is intentionally absent
until then, the harness is wrong and should assert what the page does show. Say which and why in last.md.

Constraints: tests on main at d94c191 stay untouched; this branch's own tests move with it. Do not touch files
outside the night page, its client script and its tests.

Done when: the command above passes in full on the host (report the sandbox-denied cases honestly as before),
`bin/lint` ok, committed, not pushed.
