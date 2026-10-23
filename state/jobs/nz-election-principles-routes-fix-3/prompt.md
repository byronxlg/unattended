# Follow-up 3: source note below the fold

Fix-2 de99f7a cleared HOME_MARKET_HEIGHT. The host harness (`PYTHONPATH=. uv run python site/build_review.py`,
then `screenshots.py --site site`, Chromium) now stops at:

    screenshots.py:221 fold_check (state earlier-coherent-window)
    SOURCE_NOTE_BELOW_FOLD: 360px bottom=835.56px viewport=780px

Cause: `web/templates/source-note.html` turned "Source history and legal method" from a
disclosure into an open block, so `#source-seats` on home grew by about 56 px at 360.

Do:
1. Keep `#source-seats` inside 780 px at 360 and 390 in that state, with the fold check unchanged.
   Suggested direction (your call): the source note keeps one short line plus `p.source-actions`;
   the contributor history and Electoral Act links move to Methods (principle: provenance to
   methods) and stay reachable from the note's Method link. Attribution (Wikipedia contributors,
   CC BY-SA 4.0, revision link) stays in the note. Every route that uses the template must still
   pass its own checks.
2. Audit, before you stop, every assertion in `tests/screenshots.py`, `market_checks.py` and
   `coalitions_browser.py` that depends on element height, position or fold on any page this
   branch changes, and list each with why it still holds. Three rounds in a row failed on a
   host-only check the previous audit did not cover.
3. A no-Chromium check (same style as market_budget_checks.py) that fails on de99f7a and passes
   on HEAD, for the source note's content size on home.

Protected: tests on main at c6d8ff3 stay unchanged and nothing weakens; this branch's own tests
move with it. Done when: product tests pass, `verify all` PASS all, `bin/lint` ok, the new check
fails on de99f7a. Commit in the worktree, do not commit last.md, do not push.
