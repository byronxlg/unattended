# nz-election-home-stale fix-2 (follow-up on the build thread)

Host Chromium run of 66a4e99 (your sandbox could not run it):
`uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_home_handover.py product/nz_election/tests/test_night_page.py`
gives 3 failed, 61 passed: test_browser_handover[zero], [complete], [recovery], all at
home_handover_browser.py:45 `page.locator('#home-night').inner_text()`:

    strict mode violation: locator("#home-night") resolved to 2 elements:
      1) <figure id="home-night" aria-describedby="source-night"> aka get_by_text("0 national seats reported.0.0")
      2) <figure id="home-night" aria-describedby="source-night"> aka get_by_role("figure").filter(has_text="Wed 21 OctOverseas voting")

So the live home DOM holds two elements with id `home-night` once results arrive (the results figure
and the pre-results dates figure). Duplicate ids are a product defect (invalid HTML, ambiguous
aria-describedby targets), not only a harness problem. Find where the second one comes from
(pipeline/home.py:204, web/home-live.mjs:38 settled/innerHTML swap) and make the rendered page hold
exactly one `#home-night` in every state; the harness keeps reading `#home-night`. Add an assertion in
your branch's browser harness that `#home-night` count is 1 before and after the cutoff. Do not edit
tests that exist on main at 3babf1e's base (e853b84); your branch's own harness files move with it.

Done: the command above passes on the host (state which Chromium cases your sandbox denied), lint ok,
commit, do not push.
