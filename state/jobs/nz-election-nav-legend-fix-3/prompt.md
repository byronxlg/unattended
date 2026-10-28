# Follow-up 3: nz-election-nav-legend (fix round)

fddc5df holds on the host (163 passed incl. Chromium; current link inside the nav at 360/390/1280 on
home, electorates/, night/). The fresh review (PR #115) asks for two checks that the branch's
mechanism needs, because links are hidden with opacity:

1. Same-page resize: on electorates/ (a trailing current route), load at 390, resize to 844 (rotation)
   and to 1280 (past the desktop breakpoint), then back to 390, without reloading. After each step:
   the aria-current link is whole inside the nav's visible box and painted (computed opacity 1,
   visibility visible), no link is shown partly, the header height is the same as on a fresh load at
   that width, and no link is left at an intermediate opacity after crossing the breakpoint. Repeat
   once with a nav link focused before the resize.
2. Keyboard and manual scroll: after each Tab and Shift+Tab through the nav at 360 and 390, the
   focused link is whole inside the nav box AND painted (opacity 1, visibility visible), not only in
   bounds with an outline. After a manual scroll of the nav (scrollLeft set, scroll event), every link
   that is shown is whole and every partly overlapped link is not painted.

If a check finds a real defect, fix the mechanism (header-nav.js or CSS) rather than the check.
Tests on main at the PR base are protected; this branch's own tests (header_nav_browser.py) move with
it. Do not pin markup, class names or byte counts. Legend work stays as is.

Done when committed (not pushed):
  uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav" -> all pass
  (list Chromium sandbox denials separately), bin/lint -> lint ok. In last.md, name each new check and
  say whether it fails on fddc5df.
