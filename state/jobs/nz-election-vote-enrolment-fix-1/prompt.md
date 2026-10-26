Fix-1 for PR #100 (vote/ enrolment copy after the close), from the fresh review.

Item: product/nz_election/pipeline/vote_page.py:43 raises KeyError 'source_url' when the enrolment record has no source_url at or after the close. Invariant: a sparse enrolment record never crashes the vote/ build; at and after the close the closed message still renders, and the source link is omitted when there is no URL (never an empty or placeholder link). Choose the shape yourself.

Add one regression test in the branch's own vote tests that fails on the current head and passes after. Tests on main at the base sha stay untouched; the branch's own tests may move. Tests check text, source URLs and absence, not markup.

Done when: `uv run --with pytest pytest -q product/nz_election/tests -k vote` passes, `bin/lint` passes, the new test fails with vote_page.py at the current head. Commit in this worktree; do not push. Report the commit sha and the test output in last.md.
