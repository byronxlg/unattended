# Eval: release-date sort metadata preserves visible fieldwork

Origin: hourly refresh failed on revision 1381086195 with invalid_dates for the
Freshwater poll conducted 9-19 October 2026, sorted by its 20 October release date.

Inject a synthetic national row into validated pinned fixture text in memory.
Visible fieldwork must win over sort metadata up to seven days after fieldwork ends,
with a diagnostic containing the source revision, row locator and reason. Earlier,
out-of-bound and malformed sort dates must still fail with invalid_dates.
Fixture bytes and existing documented exceptions remain unchanged.

Run `evals/polls-release-date-sort/check.sh` offline. Expected final line:
`PASS release-date row parsed`. The row must span 2026-10-09 to 2026-10-19.
