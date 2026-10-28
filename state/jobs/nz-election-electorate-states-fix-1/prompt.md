# Fix 1: PR #128 electorate post-close states

Fresh review of PR #128 (state/jobs/review-nz-election-electorate-states/last.md) asks for changes; the supervisor confirmed each at the lines named.

1. `product/nz_election/pipeline/electorate_pages.py:86`: the section subtitle "Candidates for your electorate vote." stays after polling close. After close it must read retrospectively (past tense), like the title already does. Test its absence after close.
2. `product/nz_election/tests/test_electorate_page_plan.py:312`: add an explicit case after close with no result capture (clock `2026-11-07T06:00:00Z`): retrospective candidate wording, and no result, leader, margin or capture claim in the visible text.
3. `test_electorate_page_plan.py:343`: the settled and official checks must assert the selected electorate's exact margin and voting-place coverage values taken from its capture, not only the labels.
4. `electorate_pages.py:88`: the candidate source date `'20 October 2026'` is a literal. Take it from the candidates snapshot's own retrieval/provenance field (read `snapshot_views.footnote` and the snapshot loader to find it); if no such field exists, say so in last.md and leave it.

Constraints: tests on main at the base sha are protected; this branch's own tests move with it. Tests check visible text and data, not markup or class names. No other files beyond what these items need.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_electorate_page_plan.py product/nz_election/tests/test_electorates.py product/nz_election/tests/test_electorate_policy_links.py` passes (list any sandbox-denied browser cases), the new cases fail with `electorate_pages.py` at 752b8e8, `bin/lint` prints lint ok. Commit in the worktree, do not push. Report in your final message; do not commit last.md.
