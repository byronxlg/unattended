# Follow-up 2: nz-election-nav-legend (fix round)

17d5f7f does not hold on the host. Origin/data build, Playwright Chromium (the version our tests use),
header nav measured by getBoundingClientRect after load:

- 390 night/: nav box 16..354; "Night" (aria-current=page) at 436..490, off screen; "Electorates"
  at 289..389 renders as "Electora" cut mid-word (screenshot: state/jobs/nz-election-nav-legend-fix-2/nav-390-night.png).
- 360 and 390 electorates/: "Electorates" (current) at 289..389, past the nav's right edge 324/354.
- 1280: fine.

So `scroll-initial-target` and the view-timeline hiding are not effective in the browser we ship
tests against. Invariants, at 360, 390 and 1280 on every route:
1. The aria-current link is fully inside the nav's visible box on load, without user action.
2. No link is shown partly: each label is either fully visible or fully hidden/scrolled away.
3. Without JavaScript the nav still works (horizontal scroll is acceptable); with it, 1 and 2 hold.
Choose the mechanism (a few lines of inline script setting scrollLeft is acceptable; so is any CSS
that Playwright's Chromium honours). Do not rely on features the test browser lacks.

The checks in screenshots.py or the design tests must measure 1 and 2 by geometry on electorates/
and night/ at 360 and 390, and must fail on 17d5f7f. Tests on main at the PR base are protected;
this branch's own tests move with it. Do not pin markup or class names.

Done when committed (not pushed):
  uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"  -> all pass
  (list Chromium sandbox denials separately) and bin/lint -> lint ok. Legend work stays as is.
