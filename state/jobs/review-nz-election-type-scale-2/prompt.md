Fresh-context review of PR #93 (nz-election-type-scale), read-only. Worktree .worktrees/nz-election-type-scale,
branch change/nz-election-type-scale, head b59240e on main 01b25d7. Diff: git diff origin/main...b59240e.
Judge against REVIEW.md, including pass 4 against intent/nz-election/pages/parties.md and product/nz_election/DESIGN.md.

The change (Byron, issue #92: "a lot of small text; promote the party funding total out of its paragraph"): type
tokens in web/styles.css with a 16 px floor for reading text; every font-size in the five CSS files uses a token or
inherits; parties/ shows the donations total as a headline figure with its caveat. Check: no reading text (sentences,
answers, list items, table cells a reader reads) is left on --fs-caption or a smaller literal; caption is only on
credits, source lines, chart notes and dense labels; nothing overflows horizontally at 360 from the larger sizes
(long tokens, tables, chips, nav); SVG text scaling stays readable; the funding figure keeps provenance (EC link,
the "not total party funding" caveat adjacent, the 20,000 threshold before the total as the campaign checks want);
the three moved test assertions pinned literal px values only and nothing that checked data, provenance or
accessibility was removed. Supervisor host run: origin/data build PASS build: 81 routes; screenshots of home,
polls, parties, vote, electorates/wellington-bays at 390 and 1280 at /tmp/ts/shots/*.png (read them). Do not run
pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.

Second round. The first review (PR #93) asked for SVG text at or above 12 px at 360 (map 11.26, trend 10.93); host
browser tests also found the header links out of bounds or under 44 px. Fix b59240e: header links wrap at 16 px with
44 px targets, SVG labels enlarged and repositioned, new rendered-size test (tests/type_scale_browser.py via
test_design.py). Supervisor host: test_design.py and test_night_page.py 55 passed with Chromium; the new test fails on
679e2fc (map 11.26, trend 10.93); origin/data build PASS 81 routes, home at 360 and 390 at /tmp/tsf/home-*.png (read
them). Check that the fix resolves both, that the new test measures rendered size not markup, and anything else the
fix introduced. Verdict: accept or request changes, findings with file:line.
