Committed `40258c2`, never pushed.

Changed `vote_page.py` and `styles.css`: local date-source credits, content-sized help rows, secondary deadline styling using existing tokens.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py
5 failed, 136 passed in 37.40s

bin/lint
lint ok (1158 text files)
```

Incomplete:
- Two unchanged action-URL tests reject the requested date-source links. Stopped rather than weaken tests.
- Sandbox denied Chromium for `map`, `trend`, and `header` checks and screenshot capture. No visual verification.

Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-vote-nits/last.md), left uncommitted.