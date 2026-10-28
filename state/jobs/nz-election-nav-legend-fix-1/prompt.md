Follow-up 1 on nz-election-nav-legend (789e2bd). Legend change accepted (TOP under "Other parties", blocs together).

The phone nav is not: at 390x844 each label now takes half the row (Overview 16-185, Polls 185-354), so only two of
seven sections show and the gaps read as broken. Supervisor measured on a host build from origin/data.

Goal: at 360 and 390, at rest, as many labels as fit at their natural width (no stretched slots), each one either
wholly visible or wholly under the existing scroll cue, never cut mid-word; at least four labels visible at 390; the
current page's label scrolled into view on every route (check electorates/ and night/). 1280 unchanged.

Your own bounding-box check in tests/screenshots.py moves with this (it is this branch's test): it must fail on
789e2bd for the two-label layout (fewer than four visible) and on origin/main for the mid-word clip. Do not edit tests
that exist on origin/main. Keep DESIGN.md true. Files: web/styles.css, tests/screenshots.py, DESIGN.md.

Done: uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav" all pass except
Chromium sandbox denials you list; bin/lint ok; commit, do not push.
