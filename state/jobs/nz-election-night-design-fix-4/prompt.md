Follow-up 4 on change/nz-election-night-design (head a12a058). Three items. Fix job: tests on origin/main at the merge base
are protected (do not weaken them); the branch's own tests (test_night_design_followup.py, and the lines this branch added
to test_night_page.py) move with it.

1. Merge origin/main into the branch (a merge commit, no rebase, no force-push). PR #95 (338fa7a) changed
   product/nz_election/tests/night_live_browser.py and it conflicts with this branch. Resolve by keeping every assertion
   main has there and re-applying only what this branch needed (selectors that moved with the new night/ layout). If a
   main assertion cannot hold with the new layout, stop and say which, do not delete it.

2. Fresh review, Important, night_electorates.py:100: the `.night-map-key` wrapper holds both "Provisional leaders, not
   elected members" and the original-boundary / no-vote-transfer caveat, and the existing search handlers hide the whole
   wrapper while filtering, so the caveats vanish during a search. Before this branch they stayed visible. Keep those
   caveats visible while a search is active (move them outside what search hides, or narrow what search hides; your
   choice). Add a browser check: with a search filter applied on night/, both caveat texts are visible.

3. Fresh review, Important: test_night_design_followup.py:49, 56-58, 82-84 and test_night_page.py:242 pin exact class
   names, HTML strings, element structure and serialized markup order. House rule (CLAUDE.md): tests check data,
   provenance, absence and accessibility, never markup. Rewrite those assertions to check behaviour instead: rendered
   order in the browser (search box top above the first majority card at 390, as result_states_browser.py does by
   bounding box), dot counts and wedge data, accessible names, visible text. Do not lose coverage of what they meant.

Done when, with Chromium if your sandbox allows (say so if not):
  uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night*.py \
    product/nz_election/tests/test_design.py product/nz_election/tests/test_home*.py product/nz_election/tests/test_waterfall*.py
  all pass; bin/lint ok; `git merge-tree --write-tree origin/main HEAD` exits 0. Commit, do not push, do not commit
  last.md or artifacts/.
