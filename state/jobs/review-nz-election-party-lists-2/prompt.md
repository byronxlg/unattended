Second fresh-context review of PR #87 (nz-election-party-lists), read-only. Worktree .worktrees/nz-election-party-lists,
branch change/nz-election-party-lists, head e9efa3d. Diff: git diff origin/main...e9efa3d; fix round: git diff 6ebf8bb e9efa3d.
Judge against REVIEW.md, including pass 4 (the question test) against intent/nz-election/pages/parties.md.

The first review (state/jobs/review-nz-election-party-lists/last.md) requested changes: partial records with empty
candidate lists must validate, and the list counts must carry their EC source note (link, licence, retrieval date,
aria-describedby). Check both are fixed, the two new regressions in test_parties_lists.py would fail on 6ebf8bb, and
nothing else regressed: every size and name traces to an EC URL in the snapshot, unconfirmed fields render nothing,
the validator still rejects malformed ranks, count/list disagreement where the list is complete, and off-domain sources;
no test on main at 3ee6372 weakened.
Supervisor host run on e9efa3d: test_parties*.py and test_snapshots.py 117 passed incl. Chromium, PASS campaign.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
