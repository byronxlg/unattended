# Fix brief: nz-election-polls-fix-1 (hourly poll refresh failing on a documented date exception)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
Worktree: .worktrees/nz-election-polls-fix on branch change/nz-election-polls-fix, base main
8a5392d. Commit there; never push. This is a fix job: tests that exist on main at 8a5392d do not
change; tests this branch adds are yours. Nothing weakens a check to pass.

## Incident

"NZ election hourly" has failed every run since 2026-10-17T07:00Z (runs 39011994985, 39029509938)
with `FAIL refresh: parse_drift`. The polls status row is stale, last good 01:20Z. The log and
the status row name only `parse_drift`; the supervisor reproduced on the host to find the cause:
`invalid_dates`, locator `8–11 Aug 2026 / 2026-08-12`, the 1 News–Verian row. That row has a
documented exception in product/nz_election/config/party-map.json (`date_exceptions`), but the
entry is keyed to revision 1380524613, the fixture's. Wikipedia moved to 1380694545 at 08:21Z
(an edit elsewhere on the page) and the exception stopped matching. Read first:
evals/polls-date-exception-revision/task.md and check.sh (committed on this branch, fails today),
product/nz_election/pipeline/poll_parser.py (dates() and the date_exceptions loop around line
285 to 300), product/nz_election/pipeline/refresh.py (the except ValueError block and main()),
product/nz_election/config/party-map.json, product/nz_election/tests/test_poll_parser.py
(test_pinned_wikitext pins diagnostics['date_exceptions'][0]['sort'] == '2026-08-12' and the row
with fieldwork_end 2026-08-11; both stay true), REVIEW.md.

## Invariants (you choose the shape)

1. A documented exception describes a row, not a page revision: a row whose visible date text,
   pollster and data-sort-value match an entry parses on every revision that carries it. The
   visible fieldwork dates win, as the existing entry already decides. An entry keeps an explicit
   source and reason (product AGENTS.md: no silent corrections). A mismatch that no entry
   documents still raises ParseDrift; a sort value or visible text that is not a date still raises.
   Do not change the fixture bytes.
2. A parse_drift outcome names its reason and locator where an operator reads: the Actions log
   line (`FAIL refresh: parse_drift ...`) and the step summary. The status row's public message
   may stay as it is or carry the reason; never a response body or anything but the row's
   locator. refresh.py's except block has the exception in hand; the status dict carries
   error_code only today.

## Definition of done

- `evals/polls-date-exception-revision/check.sh` last line
  `PASS exception row parsed on revision 9999999999`.
- `uv run --with pytest pytest -q product/nz_election` all pass (main at 8a5392d: 372 passed;
  your new tests add to that, none removed or edited).
- `bin/lint` prints nothing but ok lines.
- One or more commits on the branch; `state/jobs/nz-election-polls-fix-1/last.md` is NOT
  committed. Your final message: what changed and why in five lines, the three command outputs
  verbatim (last lines), and anything you chose not to do.
