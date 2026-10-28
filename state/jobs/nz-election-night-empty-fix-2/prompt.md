# Follow-up 2: fresh review of PR #129 requests changes

The fresh review (read-only, REVIEW.md) found, and the supervisor confirms:

1. Important: `product/nz_election/tests/night_empty_browser.py:57` checks the waiting message but never asserts the absence of election figures. Before the first capture, after an empty response, and in the ended state, assert that no seat totals, reporting percentage, vote counts or electorate leaders are shown (check visible text and data, e.g. no digits-with-seat/percent wording in the results region, no leader rows), and find the waiting message by its accessible status role (`get_by_role("status")`), not by markup.
2. Nit: the raw markup substring assertions this branch added in `test_night_page.py:13` should become behaviour checks (visible text, roles) or go. Tests on main at base sha 1c495f3 are protected; this branch's own tests move with it.

Show each new absence check failing against a deliberately injected figure (a quick local mutation you revert, reported in your message), not committed.

Done when: `uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_design.py` passes (list sandbox-denied browser cases), `bin/lint` prints lint ok. Commit in the worktree, do not push, do not commit last.md.
