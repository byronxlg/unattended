Follow-up 1 on 7732c4d (supervisor host verification, 2026-10-18 23:45Z).

Host results: 674 passed, lint ok, verify all PASS, measure_home PASS (details 0, links 37,
source 7, 10,699 bytes, h2 7). The screenshot harness FAILS on the host (Chromium runs here):

  uv run product/nz_election/tests/screenshots.py --site artifacts/site --out artifacts/nz-election/screenshots
  AssertionError: PAGE_OVERFLOW: http://127.0.0.1:.../unattended/nz-election/downloads/

At 360 px document scrollWidth is 284,685. Cause: build.py now passes every page through
markup.open_prose, a regex that turns every <details> on every route into an open <div>. On
downloads/ that exposes the raw envelope JSON (tokens of 11,250 characters, `{"bytes":3202023,
"fetched_at":...`) inside table.download-catalogue. The same rewrite changes every other route.

Fix, as a build round on this branch:
1. Remove the sitewide HTML rewrite (open_prose and its call in build.py). design-principles.md
   principle 2 asks for zero <details> on the home page only, and allows them on other routes for
   long tables. Reach zero on home in the home templates/renderers, not by rewriting output.
   Other routes keep the disclosures they had on main at b0f3b3f unless a principle names them.
2. Raw JSON never appears as visible prose on any route.
3. The phone menu was removed and the desktop nav is shown at all widths. Keep that only if the
   header fits at 360 and 390 without overflow and with 44 px targets; otherwise keep the phone
   menu. Either way the no-JS navigation check in screenshots.py tests what ships, never weaker.
4. Add a check (verify or a test over the built fixture site) that fails when any route's visible
   text contains a whitespace-free run over 200 characters; show it fails on 7732c4d.

Tests on main at b0f3b3f that pinned sitewide disclosures move only where item 1 says the route
changes; the branch's own tests move with it.

Done when: pytest passes, bin/lint ok, verify all PASS, measure_home PASS with the numbers
printed, the new check printed failing on 7732c4d and passing on the fix. Chromium is blocked in
your sandbox: say so, and the supervisor runs the harness on the host. Commit, do not push, do
not commit last.md or artifacts/.
