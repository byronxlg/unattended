# Build: two backlog nits (funding ranking, landmark test)

Page plan: intent/nz-election/pages/funding.md. Design: product/nz_election/DESIGN.md (no visual change intended).

Goal: two items from state/design-backlog.md (27 Oct 09:22Z, PR #108/#109 review nits), now that the nav work has merged.

1. `funding_page.ranking()` duplicates `home_graphics.funding_bars()` with different rounding, so home and
   funding/ can show different totals for the same party. One function computes the per-party totals and
   their rounding; both callers use it. The invariant: for every party, the total shown on home equals the
   total shown on funding/ (whole NZD). Add a test that builds both from the same donations data and
   compares the numbers per party (data, not markup).
2. `product/nz_election/tests/test_design.py` around line 237 matches literal `<header>`/`<footer>` tags.
   Parse landmarks structurally (html.parser or the existing parser helpers): a page has exactly one
   banner header and one contentinfo footer regardless of attributes. This test may change (build job);
   it must still fail on a page with no header or two footers (show that with a case).

Read first: product/nz_election/pipeline/funding_page.py, pipeline/home_graphics.py, tests/test_design.py,
tests touching funding (rg -l funding product/nz_election/tests).

Constraints: no markup, class or style changes; tests check data and structure, not markup or bytes.
Tests on main at the base sha may change only for item 2 and for any assertion that pinned the old
duplicated rounding (name it in your summary).

Done when, from the worktree root:
`uv run --with pytest pytest -q product/nz_election/tests -k "funding or design or home_graphics"` passes,
and `bin/lint` prints ok. Commit; do not push. Summary lists any totals that changed and by how much.
