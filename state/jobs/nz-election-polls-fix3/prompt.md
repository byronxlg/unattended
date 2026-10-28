# Build: documented date exceptions must cover a sort value before fieldwork end (polls incident 28 Oct)

## What broke
"NZ election hourly" run 40760666619 (2026-10-28T20:09Z) failed: `FAIL refresh: parse_drift ... {"reason": "invalid_dates", "locator": "table:15/row:2"}`. Polls are stale on the live site ("update failed; showing previous data"). Reproduced on the host with `refresh.py`. Wikipedia revision 1382442932 added an RNZ–Reid Research row:

    | data-sort-value="2026-10-01" |'''20–26 Oct 2026'''
    |[https://www.rnz.co.nz/news/politics_election-2026/2211553/... RNZ–Reid Research]

The visible fieldwork dates are right (20 to 26 October; RNZ published it after); the sort value is an editor typo, 25 days before fieldwork end. `poll_parser.dates()` raises `invalid_dates` for a sort before the end (`poll_parser.py:210`), and it is called (`:312`) before the documented-exception loop (`:314`), so a documented exception in `config/party-map.json` `date_exceptions` can never rescue such a row. One mis-sorted row fails the whole refresh.

## Invariant
A row matching a documented exception in `party-map.json` (visible text, sort value, pollster, source, reason; not a revision) parses on its visible fieldwork dates whatever its sort value says, and is listed in diagnostics as a documented exception. An undocumented row whose sort value is before fieldwork end or more than MAX_RELEASE_LAG_DAYS after it still fails with `invalid_dates` exactly as now (main's tests pin this: test_poll_parser.py:92, test_release_date_sort.py:51,63, test_date_exception_revision.py). You choose the code shape.

Then add the documented exception for this row to `date_exceptions` (source `https://en.wikipedia.org/w/index.php?oldid=1382442932`, reason stating visible fieldwork 20 to 26 Oct is retained and the sort value disagrees).

## Files to read first
`product/nz_election/pipeline/poll_parser.py` (dates, parse_polls around :300-335), `product/nz_election/config/party-map.json`, `evals/polls-date-exception-revision/` and `evals/polls-release-date-sort/` (shape of an eval), the three test files named above. Live wikitext is saved at `state/jobs/nz-election-polls-fix3/wikitext-1382442932.txt` in the main checkout (read-only for you; copy what you need).

## Constraints
- Tests on main at the base sha are protected: do not edit them. Add new tests.
- Add `evals/polls-exception-sort-before-end/` (task.md naming the incident and invariant, check.sh) whose check fails on origin/main and passes on your branch. Use a small fixture built from the row above, not the whole page.
- No other behaviour changes. No network in tests.

## Done when
- `uv run --with pytest pytest -q product/nz_election/tests/test_poll_parser.py product/nz_election/tests/test_release_date_sort.py product/nz_election/tests/test_date_exception_revision.py` plus your new test file: all pass.
- `bash evals/polls-exception-sort-before-end/check.sh` last line PASS; the same check against origin/main's poll_parser.py fails.
- Parsing the saved live wikitext with the branch's parser and config yields no ParseDrift and includes the RNZ–Reid Research row with fieldwork end 2026-10-26.
- `bin/lint` prints lint ok. Commit in the worktree; do not push; do not commit last.md.
