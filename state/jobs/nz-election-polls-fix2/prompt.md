# Fix brief: nz-election-polls-fix2 (hourly poll refresh failing on a new poll's release-date sort value)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
Worktree: .worktrees/nz-election-polls-fix2 on branch change/nz-election-polls-fix2, base main
57063db. Commit there; never push. Tests on main at 57063db do not change and nothing weakens a
check; tests and the eval this branch adds are yours.

## Incident

"NZ election hourly" has failed every run since about 20:40Z 19 Oct with
`FAIL refresh: parse_drift ... {"reason": "invalid_dates", "locator": "table:15/row:2"}`; polls
are stale on the live site. The supervisor reproduced on the host against live revision
1381086195 (saved, read-only for you: /tmp/pollprobe/live-1381086195.json, the API parse JSON;
wikitext at .parse.wikitext): a new national poll row

    | data-sort-value="2026-10-20" |'''9–19 Oct 2026'''
    |[https://www.thepost.co.nz/politics/361101225/... The Post/Freshwater Strategy]
    | 1,458 || 27.6 || ... 28.7 || 14.3 || 9 || 11.8 || 2.0 || 5.4 || –

Fieldwork ends 19 Oct; the sort value is the release date, one day later. This is the same class
as the 1 News-Verian exception in config/party-map.json `date_exceptions` (sort 2026-08-12 for
8–11 Aug), which needed a hand entry. A hand entry per new poll means the hourly breaks every time
a pollster publishes the day after fieldwork. Read first: product/nz_election/pipeline/poll_parser.py
(dates(), the date_exceptions handling in _parse_polls), refresh.py, party-map.json,
tests/test_poll_parser.py, evals/polls-date-exception-revision/, REVIEW.md.

## Invariants (you choose the shape)

1. A row whose data-sort-value is a date a short, bounded number of days AFTER the visible
   fieldwork end (release-date convention; pick the bound, at most 7 days, name it as a constant
   with a comment) parses: the visible fieldwork dates win, and the row is recorded in the parse
   diagnostics (as the documented exceptions are) so the substitution is never silent. A sort value
   before fieldwork start, more than the bound after the end, or not a date still raises ParseDrift
   invalid_dates. The existing documented exception keeps working and its pinned test stays true.
2. Fixture bytes do not change.

## Eval and tests

- New eval evals/polls-release-date-sort/ (task.md, check.sh, same shape as
  evals/polls-date-exception-revision): offline; inject the row above (or one built the same way)
  into the pinned fixture wikitext and parse; last line `PASS release-date row parsed` with the
  row's fieldwork 2026-10-09 to 2026-10-19. Show it failing on 57063db (run it before the fix,
  quote the FAIL line in your report).
- Unit tests for the boundaries: +1 day passes, bound+1 day raises, before start raises.

## Definition of done

- the new eval PASS; evals/polls-date-exception-revision/check.sh still PASS.
- A host-side check of the live file: parse /tmp/pollprobe/live-1381086195.json's wikitext with
  revision 1381086195 and print the row count and that a 2026-10-19 Freshwater row exists.
- `uv run --with pytest pytest -q product/nz_election` all pass; `bin/lint` ok.
- Commits on the branch; last.md not committed. Report: what changed in five lines, command
  outputs (last lines), what you chose not to do.
