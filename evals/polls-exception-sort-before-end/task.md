# Eval: documented sort value before fieldwork end

Incident: NZ election hourly run 40760666619 at 2026-10-28T20:09Z failed with
`parse_drift`, reason `invalid_dates`, locator `table:15/row:2`. Wikipedia revision
1382442932 added RNZ–Reid Research fieldwork 20–26 Oct 2026 with a sort value of
2026-10-01. Validation ran before documented exceptions could rescue the row.

Invariant: an exact documented exception (visible text, sort value, pollster,
source and reason) retains visible fieldwork dates and emits a documented-exception
diagnostic across revisions, even when sort metadata precedes fieldwork end or
exceeds MAX_RELEASE_LAG_DAYS. Undocumented out-of-bound dates still fail with
invalid_dates. Malformed dates and reversed fieldwork remain invalid even when
an exception matches.

The small row.wikitext fixture contains only the incident row and national headers.
Run `bash evals/polls-exception-sort-before-end/check.sh` offline; last line: `PASS`.
Run the same check with `origin/main` as an argument to load only that ref's parser
against the branch's fixture and config; it must fail with invalid_dates.
