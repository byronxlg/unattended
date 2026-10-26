# vote/ polish fix-1 (PR #102, fresh review request changes)

Same worktree and branch as your build (.worktrees/nz-election-vote-polish, change/nz-election-vote-polish, head f728f4d). Read `product/nz_election/DESIGN.md` and `intent/nz-election/pages/vote.md` again before editing.

Fix these three findings from the fresh review of f728f4d:

1. `product/nz_election/pipeline/vote_page.py:86`: after the enrolment close (from 26 Oct 00:00 NZDT) the help deadline is skipped as "already shown", but the closed-state answer says only "The enrolment close has passed" and the timeline drops the time. The exact deadline (date and time, from the snapshot) must still be visible once in every phase.
2. `vote_page.py:108`: deduplication covers only help entries. Election-day 7pm close still appears in the timeline and in help (and the countdown on election day). Invariant: each deadline's exact date and time is stated once in the page's visible text, in every phase (before, advance, election day, after). A live countdown is a separate element and may stay. You choose where the single statement lives.
3. `vote_page.py:126`: a record without `retrieved_at` raises KeyError (also in the parent's date/global credits). A sparse record renders without a crash and without a dangling `aria-describedby` or an empty "retrieved" line.

Constraints:
- Tests on `change/nz-election-vote-nits` at 76b5126 are protected: do not edit them. Tests this branch added (since 76b5126) may move with the change. Add tests for the three invariants that check visible text and absence, not markup or class names; each must fail on f728f4d.
- No new data sources. Commit in the worktree, do not push.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests -k vote` passes (Chromium cases may be sandbox-denied; say which).
- `bin/lint` prints ok.
- In last.md: the commit sha, the new tests and that they fail on f728f4d, and for each phase the one place each deadline is stated.
