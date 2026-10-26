# Follow-up 1: vote-nits

You stopped correctly. The brief asked for local source links without checking main's contract; that is
the supervisor's error, not yours.

The invariant stays: everything before `<section id="help">` links only to snapshot action `url` values on
vote.nz or elections.nz (`product/nz_election/tests/test_vote_page.py:44`). The first screen is actions.

Change item 1 so it holds: the countdown and timeline feet name their source near the content without a
link to a `source_url` (for example the source title and retrieval date as plain text, or a pointer to the
full credit below). The complete linked credit below help stays as is. Choose the shape; do not edit tests.

Items 2 and 3 stand as committed.

Done when, in this worktree:
- `uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py`
  shows no failures other than the three sandbox Chromium launches;
- `bin/lint` prints `lint ok`;
- one commit on top of 40258c2; `last.md` and `artifacts/` not committed; no push.
