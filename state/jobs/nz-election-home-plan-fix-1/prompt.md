Fix-1 on PR #64 (home rebuild from intent/nz-election/pages/home.md). Supervisor review and a fresh review both request changes; one round covers both lists.

Page plan: intent/nz-election/pages/home.md

Do:
1. Question test at 390x844 (pages/home.md fold): the answer to question 2 (how polls changed: the party movement sentence or figure, not only its heading) must sit above the fold together with the answers to questions 1 and 3. Shorten or reorder above the fold; do not drop Q1 or Q3 answers.
2. Mobile electorate picker: at 360 and 390 the map and the list must not share equal columns (targets shrink to about 9x9 px). Stack them or give the list full width so every electorate link is at least 24x24 CSS px. Extend the target-size check so it covers the picker's SVG links rather than excluding them, and show that check failing on cf770ea and passing on your HEAD.
3. Closest-margins module: the hex markers read as detached from the rows. The loose column is the seven Maori electorates; label it directly, or tie each row to its marker so a reader can tell which is which.
4. test_home_defects.py:73 exercises market_graphic(envs), which the moved module no longer renders. Point that test at what is rendered (Methods uses market_panel.panel) with assertions identical or stronger.
5. Remove the duplicate directory link on home (home.py:372: keep one of "Browse all electorates and candidates" / "See all electorates").
6. Harness blocker on main: methods/ at 360 fails SMALL_TARGET on the overdue band's inline "Update details" link (build.py:296 and :303, electorate_pages.py:54/56). Make that link a target that passes the existing size rule (for example its own line in p.source-actions); do not loosen the rule.

Tests on main at de9a7c2 are protected: do not weaken or delete their assertions. Tests this branch added move with it.

Done when: `uv run --with pytest pytest -q product/nz_election/tests` passes, `bin/lint` ok, `python -m product.nz_election.pipeline.verify all` PASS on a populated build, and the screenshot harness passes home/ and methods/ at 360, 390 and 1280. last.md lists the 390 fold answers for Q1 to Q3 as visible text and the failing-then-passing evidence for item 2. Commit in the worktree, do not push, do not commit last.md.
