Fresh-context review of PR #69 (nz-election-social-retry), read-only. Worktree .worktrees/nz-election-social-retry,
branch change/nz-election-social-retry, head 27dee94. Diff: git diff main...27dee94. Judge against REVIEW.md.

Context: the 2026-10-23 social daily spent the exact 24-page allocation (7,560 credits) when one page needed a retry,
then failed SOCIAL_CREDIT_CAP and discarded the whole day. The change publishes the fetched windows as "N of 24 hours
sampled". Check: the 7,800 cap, reservations and pre-request limits are not loosened; a partial day can never be read
as a full day (caption, status row, data envelope, social/poc/ page); windows are canonical, ordered and counts
consistent, enforced in the validator not just the writer; a run that fetched nothing still fails and retains the
prior sample; the eval evals/social-retry-budget fails on 28279a5 and passes on HEAD; moved tests in test_social.py and
test_social_publication.py were moved only where they pinned all-or-nothing publication and nothing weaker remains;
retry diagnostics carry no raw posts, handles, query text or keys.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
