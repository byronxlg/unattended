Fix round 1 on PR #48 (M3 increment 1, advance voting), same worktree .worktrees/nz-election-m3-advance and
branch change/nz-election-m3-advance, head 6bbc873. The fresh review requested changes; full text in
state/jobs/review-nz-election-m3-advance/last.md (main checkout, also on the PR). Fix all three:

1. advance.py:75-89: malformed descriptors (missing `kind`, null `start`, null `advance`) raise KeyError,
   TypeError, AttributeError, which the daily refresh does not catch (it catches ValueError), so one bad
   descriptor aborts the whole refresh. Validate descriptor shape and raise the handled INVALID_ADVANCE
   failure, so failure status publishes and unrelated families still publish. Tests for each of the three
   probes, asserting the refresh completes with the advance failure recorded.
2. m3_checks.py:20-30: with no backing rows the absence check accepts an `<h3>Advance voting</h3>`, an empty
   `<figure>`, and placeholder copy such as "No campaign totals are available here yet." Make the check
   structural: no advance heading, figure or placeholder sentence without backing rows. Negative tests for
   each, and show the strengthened check failing on a constructed page with each. Note PR #45 just merged
   to main with content_checks.py EMPTY_MODULE: if you can reuse its helper without rebasing, fine; do not
   rebase this branch, the supervisor rebases at merge.
3. campaign_page.py:9: one observation outside the hardcoded voting window hides the whole valid series
   (the committed 2023 capture has pre-opening zero rows, e.g. 25 Oct zero then 26 Oct count). Keep valid
   observations; drop or ignore only out-of-window rows, with the behaviour disclosed if a row is dropped.
   Test with the 2023 capture shape.

Contracts: tests on main at the branch base are protected; tests this branch added may move with the fix,
nothing weaker. Commit in the worktree, do not push.

Done when: `uv run --with pytest pytest -q` passes (report the count), `bin/lint` ok, and
`PYTHONPATH=. uv run python -m product.nz_election.pipeline.m3_checks` (or the branch's equivalent entry
point) passes on the populated and production fixture builds. Say in last.md which commands you ran and
their output lines.
