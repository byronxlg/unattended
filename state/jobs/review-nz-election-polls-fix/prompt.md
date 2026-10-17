# Fresh review: PR #27, change/nz-election-polls-fix

You are a fresh-context reviewer. Read `REVIEW.md` first, then review the diff of this branch
against `main` (`git diff main...HEAD`). Do not read `state/jobs/`.

Context: the "NZ election hourly" workflow has failed every run since 2026-10-17T07:00Z with
`FAIL refresh: parse_drift`. The 1 News-Verian date exception in
`product/nz_election/config/party-map.json` was keyed to fixture revision 1380524613; Wikipedia
moved to 1380694545 and the exception stopped matching, so the polls status row went stale. The
fix (beb364c) makes a date exception match on visible text, sort value and pollster across
revisions (entries must carry `source` and `reason`), and makes a parse_drift outcome name its
reason and locator in the Actions log line, the step summary and the status row message. It is a
fix job: tests on `main` at 8a5392d must be untouched; this branch's own tests may move with it.
The fixture bytes must be unchanged.

Judge: whether an undocumented date mismatch, a malformed sort value, a non-date visible text or
a fieldwork end outside 2026 still raises ParseDrift (nothing loosened beyond the documented row);
whether the exception can match a different row than intended (another pollster, another
revision's row with the same visible text but a different sort); whether `allow_sort_mismatch`
can leak into any other call of `dates()`; whether the status row message can carry anything but
the reason and the row's locator (no response body, no wikitext); whether the status row's
public shape still validates against its schema and the page that renders it; whether the eval
measures the incident (a different revision, the same fixture) and would fail on `main`; whether
any check on `main` was weakened.

Run: `bash evals/polls-date-exception-revision/check.sh`,
`uv run --with pytest pytest -q product/nz_election/tests/test_date_exception_revision.py product/nz_election/tests/test_poll_parser.py product/nz_election/tests/test_refresh.py`,
`bin/lint`.

Output: a verdict (accept, accept with nits, request changes) and a numbered list of findings,
each with severity (Important or Nit), file:line, and the precise change wanted. No praise.
