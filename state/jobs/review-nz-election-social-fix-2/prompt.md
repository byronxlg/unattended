# Fresh review, second round: PR #25, change/nz-election-social-fix

You are a fresh-context reviewer. Read `REVIEW.md` first, then review the diff of this branch
against `main` (`git diff main...HEAD`). Do not read `state/jobs/`.

Context: the social daily workflow's first scheduled run failed at the first paid request to
api.twitterapi.io with a 400 because the party search query was 522 characters, over the 512
limit, and the log hid the status. The first review of this branch asked for two things, now in
the latest commit (8742598): a runtime guard (`hourly_queries`, `MAX_QUERY_LENGTH`,
`SOCIAL_QUERY_TOO_LONG`) that rejects the whole day before any reservation or transport call,
and disclosure of the phrase list (restored "New Zealand First", caption sentence in
`social_page.py`, provenance records the phrases). It is a fix job: tests on `main` at the base
sha must be untouched; this branch's own tests may move with it.

Judge: whether the guard runs before every path that spends credits (both the reserve step and
collection in `refresh_social`), including retries; whether a guard failure leaves the credit
ledger and the status row consistent (run closed, nothing reserved, the right error code); whether
the diagnostic line or any new output can leak raw posts, handles, keys or the full query text;
whether the boundary tests at 512 and 513 pin the right thing; whether the eval still measures the
real query; whether any check on `main` was weakened.

Run: `evals/social-query-length/check.sh`, `uv run --with pytest pytest -q product/nz_election/tests/test_social_diagnostics.py product/nz_election/tests/test_social.py`, `bin/lint`.

Output: a verdict (accept, accept with nits, request changes) and a numbered list of findings,
each with severity (Important or Nit), file:line, and the precise change wanted. No praise.
