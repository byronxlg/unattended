# Fresh review: PR #25, change/nz-election-social-fix

You are a fresh-context reviewer. Read `REVIEW.md` first, then review the diff of this branch
against `main` (`git diff main...HEAD`). Do not read `state/jobs/`.

Context: the social daily workflow's first scheduled run failed at the first paid request to
api.twitterapi.io with a 400 because the party search query was 522 characters, over the 512
limit, and the log hid the status. This fix adds query headroom and safe diagnostics, plus an
eval under `evals/social-query-length/`. It is a fix job: existing tests must be untouched except
the one phrase pin the supervisor asked to change (Opportunities Party).

Judge: correctness of the length guard (is 512 the right bound, is it checked before any paid
request, every query shape covered); whether the diagnostics can leak raw posts, handles, keys or
the full query text into a log, `data/`, a page or a PR body; whether the eval would have caught
the incident; whether any check was weakened to pass; whether the phrase change alters which
posts are matched in a way the caption must say.

Run: `evals/social-query-length/check.sh`, `uv run --with pytest pytest -q product/nz_election/tests/test_social_diagnostics.py product/nz_election/tests/test_social.py`, `bin/lint`.

Output: a verdict (accept, accept with nits, request changes) and a numbered list of findings,
each with severity (Important or Nit), file:line, and the precise change wanted. No praise.
