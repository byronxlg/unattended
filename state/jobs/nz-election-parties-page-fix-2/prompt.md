# nz-election-parties-page fix-2 (PR #61, follow-up on your build thread)

Host screenshot harness on b389f5e failed `HEADING_OUTLINE` (screenshots.py:155: within `main`, h1 to h4 never skip a level) and bbbb576 still fails it. A host build of bbbb576 on live data shows `parties/index.html` main headings as `[1, 3, 3, 2, 3, 3, 2, ...]`: an h3 follows the h1 with no h2 between. Every other route of the 81 passes.

1. Fix the parties/ heading outline so no level is skipped (the picker or the first party block's h3 needs an h2 above it, or the right level). Keep the visible order and question rank from pages/parties.md.
2. Add a test that needs no browser: build the populated offline site and assert the same rule as screenshots.py:155 for every route's `main`. Show it failing on bbbb576 and passing on your commit.

Tests on main at the base sha are protected; this branch's own tests move with it.

Done when: pytest passes except the sandbox Chromium launch errors (name them), the populated `verify.py all` ends PASS all on 81 routes, `bin/lint` prints lint ok, last.md names the new test and its result on bbbb576. Do not commit last.md.
