# Fresh review, second round: PR #27, change/nz-election-polls-fix

You are a fresh-context reviewer. Read `REVIEW.md` first, then review the diff of this branch
against `main` (`git diff main...HEAD`). Do not read `state/jobs/`.

Context: the "NZ election hourly" workflow failed from 2026-10-17T07:00Z with
`FAIL refresh: parse_drift` because the 1 News-Verian date exception in `party-map.json` was
keyed to a Wikipedia revision that moved. beb364c made the exception match a row (visible text,
sort value, pollster; `source` and `reason` required) and made parse_drift name its reason and
locator in the status row message, the `FAIL refresh:` line and the step summary. The first
review found that the published locator carried raw wikitext for non-date parser failures. The
latest commit (05d9b0a) answers it: `ParseDrift.public_locator`, set only from scanner-generated
positions (`line:N`, `table:N/row:M`) by a wrapper in `parse_polls`, is the only locator that
reaches public outputs; branch tests feed marker wikitext through `refresh()` and `main()`.
Fix job: tests on `main` at 8a5392d untouched; this branch's own tests may move; fixture bytes
unchanged.

Judge: whether every path that publishes a ParseDrift (status message, SystemExit text, step
summary, anything else in refresh.py or the workflow) now uses `public_locator`; whether a
position recorded by the scanner can itself contain source text (how `line` and `locator` are
built); whether the wrapper can attach a stale position from an earlier table or row to a later
failure, and whether that is acceptable for an operator; whether the marker tests cover the
`main()` path and the summary file, not only `refresh()`; whether the incident's own row still
publishes `table:15/row:19`; whether anything on `main` was weakened.

Run: `bash evals/polls-date-exception-revision/check.sh`,
`uv run --with pytest pytest -q product/nz_election/tests/test_date_exception_revision.py product/nz_election/tests/test_poll_parser.py`,
`bin/lint`. If the sandbox blocks uv, say so and probe in memory as you can.

Output: a verdict (accept, accept with nits, request changes) and a numbered list of findings,
each with severity (Important or Nit), file:line, and the precise change wanted. No praise.
