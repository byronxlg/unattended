# Follow-up 1 on 679e2fc (PR #93: fresh review request changes, host browser tests fail)

Tests on main at 01b25d7 are protected; tests this branch added or edited move with it. Keep the 16 px reading floor and the parties/ funding headline.

1. Host: `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py` errors in setup with `HEADER_TARGET_BOUNDS` (screenshots.py:161 via night_browser.py:66): with the new type scale, a `header a` overflows the viewport or is under 44 px tall at a narrow width. Main passes this check. Make every header link fit inside the viewport at 360 with a 44 px target (wrap, tighter nav type within DESIGN.md tokens, or another layout you choose); do not change the check.
2. Review, `product/nz_election/web/styles.css:425` and `:387`: SVG text renders below DESIGN.md's 12 px minimum at 360 (map labels 11.26 px from the 466-unit viewBox; narrow trend labels 10.93 px from the 360-unit viewBox). Make rendered label size at least 12 px at 360 for both, without overlap. Add a test that measures rendered SVG text size at 360 (getBoundingClientRect or computed size times scale), and show it fails on 679e2fc.

Definition of done: `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_design.py` passes including the Chromium cases; your new test fails on 679e2fc; `bin/lint` ok. Commit in the worktree, do not push. Report the commands and their last lines in last.md (do not commit last.md).
