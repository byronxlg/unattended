Fix-3 on PR #60 (second fresh review, one Important, confirmed by the supervisor).

Problem: the active night/ renderer (pipeline/night_page.py page()) dropped the s197 publication-freeze notice that main's renderer (route_cards.night) carried: "No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197." with the Electoral Act s197 link. route_checks.py:42 now compares against the new renderer, so the gate no longer requires the notice, and test_home_routes.py:33 still exercises the unused old renderer.

Do:
1. night/ shows the freeze notice with the s197 link and the official EC results link in every phase (before results, packaged results, replay), inside its source note.
2. route_checks.check_site requires the freeze sentence and the s197 link in night/index.html as a separate named requirement ('night publication freeze notice'), in addition to the page() equality.
3. A test that builds night/ through the active path and fails if the freeze notice is missing; show it failing on eb4a0d0 (revert your renderer change locally, run it, restore) and passing on HEAD.
4. Tests on main at b523eda are protected: do not weaken or delete any assertion in test_home_routes.py. You may point test_night_transition_without_bypassing_freeze at the active renderer if its assertions stay identical or stronger. Tests this branch added move with it.

Done when: `uv run --with pytest pytest -q product/nz_election/tests` passes (Chromium installed on the host), `bin/lint` ok, `python -m product.nz_election.pipeline.verify all` PASS on a populated build, and last.md lists the failing-then-passing evidence. Commit in the worktree, do not push, do not commit last.md.
