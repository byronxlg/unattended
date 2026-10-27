# Follow-up 1 on 6ebf8bb (PR #87, fresh review request changes)

Fix two Important findings. Tests on main at 3ee6372 are protected; tests this branch added move with it.

1. `product/nz_election/pipeline/snapshots.py:493`: a partial record (verified list count, no confirmed opening names, `candidates: []`) must validate. Keep every check on confirmed lists (rank continuity, ranks within the count, truncated confirmed lists rejected). Add a test that runs the partial record through the validator and then the renderer (no bypass), and show it fails on 6ebf8bb.
2. `product/nz_election/pipeline/parties_page.py:121`: the list count needs its source treatment like the other sourced facts on the page: the recorded EC source, its copyright/licence notice and retrieval date in the source note, and `aria-describedby` from the count to that note. Follow the existing source-note pattern on the page; do not invent a new one. Add a test.

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests/test_parties*.py product/nz_election/tests/test_snapshots*.py` passes except Chromium launch failures from the sandbox (list them).
- `python3 product/nz_election/pipeline/verify.py campaign` prints `PASS campaign`; `bin/lint` prints `lint ok`.
- One commit, no push; last.md uncommitted. Screenshots are taken by the supervisor on the host.
