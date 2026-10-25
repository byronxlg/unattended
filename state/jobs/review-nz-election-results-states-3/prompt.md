Third fresh-context review of PR #79 (nz-election-results-states), read-only. Worktree .worktrees/nz-election-results-states,
branch change/nz-election-results-states, head 02940a6. Latest fix: git diff 84f8da5...02940a6; whole change: git diff c2ce1fc...02940a6.
Judge against REVIEW.md, pass 4 (the question test against intent/nz-election/pages/night.md) before any visual judgement.

The second review asked for one change: the nav label must not stay "Live preliminary results" after the settled and
official handovers (the capture pin move was accepted). Fix-2 makes the label neutral ("Latest 2026 results") with the
sequence hrefs unchanged, and adds browser assertions for both handovers plus a static regression.

Earlier items (first review): the official state must not be reachable by relabelling preliminary data; preliminary copy
must not survive the handover to official; the Q3 check runs with named leaders. Invariant: an official package names an
official source URL distinct from the preliminary feed and a source clock parsed from the XML on or after 27 November.

Check: the nav item is closed, not worded around, and no other preliminary-only copy survives a terminal handover; the
earlier items stay closed; nothing weakens an existing check; tests on main at c2ce1fc are untouched (the branch's own
tests may move). Host on 02940a6: test_result_states, test_night_page, test_night_operation 128 passed incl. browser with
host Chromium; test_current_result_navigation_has_neutral_label fails with night_page.py at 84f8da5; bin/lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
