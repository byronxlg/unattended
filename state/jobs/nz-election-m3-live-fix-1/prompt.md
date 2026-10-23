# nz-election-m3-live follow-up 1 (host verification)

The supervisor ran your branch (15744a3) on the host, where Chromium starts.

`uv run --with pytest pytest -q product --tb=short -x` : 1054 passed, 1 error, at
`test_night_page.py::test_xml_python_browser_parity` setup, which runs `night_browser.py`:

```
night_live_browser.py", line 97, in images
    assert len([u for u in requests if u.endswith('night-live.json')]) == count+1
AssertionError
```

State `live-hidden-resumed`: after the page becomes visible again, no `night-live.json` request is
seen before `networkidle`. Either `web/night-live.mjs` does not fetch on resume, or the fetch is
scheduled on a timer that `page.clock` holds (installed fake clock; a `setTimeout` on resume will
not fire until the test advances the clock). Find which, from evidence, and fix the right side:
a reader returning to the tab should get a fresh fetch at once. If the test is wrong (it waits on
real network while the fetch sits behind a faked timer), the test may advance the clock by a
bounded small amount, but it must still prove exactly one fetch on resume and none while hidden.
This test is your branch's own, so it may move; tests on main at 0a94cba may not be weakened.

Definition of done:
- `uv run product/nz_election/tests/night_browser.py <out>` exits 0 on your machine if Chromium
  starts; if it cannot, say so and the supervisor reruns it on the host.
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_night_operation.py` passes.
- `bin/lint` ok. Commit on change/nz-election-m3-live; do not commit last.md or artifacts/.
