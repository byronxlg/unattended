# nz-election-results-states fix-1 (PR #79)

The fresh review (state/jobs/review-nz-election-results-states/last.md, logged on PR #79) asks for
three changes. Fix all three on this branch; commit in this worktree, do not push.

1. Official state needs evidence from the feed itself (night_live.py:129). Today a preliminary
   capture with a later retrieved_at, a later source_updated_local and the label "Official results"
   validates as official. Invariant: a package is official only when the EC payload it was parsed
   from says so (whatever the official-count XML or its header actually carries; check the 2023
   captures and the EC feed docs in the tree), recorded in the package and checked where
   NIGHT_STATE is raised now. You choose the field and shape; read the validator and every consumer
   of the package before changing it. Add a regression test: the preliminary fixture relabelled
   and retimestamped must raise. If no capture in the tree shows what an official payload carries,
   stop and say so in last.md rather than invent a marker.
2. Handover copy (night_page.py:138, night-live.mjs:67). When the client receives an official
   package on a page built preliminary, the surrounding state copy ("Preliminary; official results
   due 27 November") must change with the snapshot. Test the real DOM transition in the browser
   test, not a helper.
3. Question three (result_states_browser.py:65). "Who is ahead in my electorate?" must be shown
   answered: a fixture with reported electorate leaders, the search returns the row, and the row
   names the leader within one scroll at 390.

Tests: tests on main at c2ce1fc are protected, move none of them; tests this branch added (739f880)
move with the change where the shape changes, nothing weaker.

Done when, from the worktree:
- `uv run --with pytest pytest -q product/nz_election/tests` passes (browser tests use host Chromium
  if present; say which ran),
- `bin/lint` prints ok,
- the new official-evidence test fails on 739f880 and passes on HEAD (show both),
- last.md lists the commits, the field you chose and why, and the test output.
