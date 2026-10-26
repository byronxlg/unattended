Fix-1 for PR #99 (vote-design), from the fresh review (state/jobs/review-nz-election-vote-design/last.md).

1. Important, product/nz_election/pipeline/vote_page.py:52: moving the timeline outside `places` breaks sparse-data heading
   parity. With voting rows containing only `advance-opens` or `advance-closes`, the timeline renders but "Where can I vote,
   and when?" disappears and the page has no h1; on main both existed. Invariant: every vote/ state that shows any answer has
   exactly one h1 and the heading for the question it answers. Add a regression test that fails on 995ac4b (sparse rows, each
   of the four phases), checking headings by role and name, not markup or class names.
2. Nit (take it if it is small): put a source link next to the countdown/timeline so provenance is near the dates.

Tests on main at the base sha are protected; this branch's own tests move with it. Keep DESIGN.md tokens, 16 px reading floor,
44 px targets. Done when `uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py`
passes (Chromium sandbox denials reported as such) and `bin/lint` is ok. Commit, do not push; commands and output in last.md.
