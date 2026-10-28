Second fresh-context review of PR #115 (nz-election-nav-legend), read-only. Worktree .worktrees/nz-election-nav-legend,
branch change/nz-election-nav-legend, base origin/main. Product diff: git diff origin/main...HEAD -- product/.
Judge against REVIEW.md and product/nz_election/DESIGN.md.

The first review asked for (1) a same-page resize check across 390, 844 and 1280 and (2) a keyboard check that does not
pass links hidden by opacity. Fix 8bc1aae adds resize, keyboard-paint and manual-scroll checks to
tests/header_nav_browser.py and sets visible links to opacity 1 with current-route priority during resize
(web/header-nav.js). Check: a clipped label is never painted partly visible; the current route stays whole in view after
resize and keyboard focus; a focused link is painted (opacity 1); tests check behaviour and geometry, not markup.
Supervisor host evidence: pytest -k "design or home or header or nav" 163 passed incl. Chromium; with header-nav.js at
fddc5df the new check fails HEADER_INTERMEDIATE_OPACITY.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
