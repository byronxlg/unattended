# Follow-up 1 (fix round): the public locator must be structural

The fresh review of beb364c (PR #27) found one Important item, accepted by the supervisor.

## Finding

`refresh.py` now publishes `exc.locator` in the status row message, the `FAIL refresh:` log line
and the step summary. For many ParseDrift sites in `poll_parser.py` the locator is text taken
from the page: `invalid_attributes` and `unexplained_merge` carry the attribute string,
`unknown_template` carries 80 characters of the template, `unknown_pollster` and
`unknown_party_mapping` carry the label or header, `invalid_dates` in `dates()` carries the
visible cell text. The reviewer reproduced a status message containing
`data-sort-value BROKEN_WIKITEXT="2026-10-14" style="background:#E8E8E8;"`. The repo, the Pages
site and the Actions log are public; nothing taken from the source body may be published there.

## Invariant (you choose the shape)

A parse_drift outcome's public outputs (status row message, `FAIL refresh:` line, step summary)
carry the reason and a structural locator (table and row indices or a line number, the form
`table:15/row:19` already used) and nothing derived from source text. Where the parser has no
structural position, the public locator is empty. The exception's own str and the pytest
matches on `main` at 8a5392d (`pytest.raises(ParseDrift, match='<reason>')`) keep working; no
test on main changes. Tests this branch added (`test_date_exception_revision.py`) may move.

## Definition of done

- A branch-owned regression test feeds malformed wikitext containing a marker string (for
  example `BROKEN_WIKITEXT`) through `refresh()` and the `main()` path and asserts the marker
  appears in none of: the status row message, the SystemExit text, the step summary file.
- The incident case still names its row: with the date exception removed, the published
  locator for the 1 News-Verian row is `table:15/row:19` (or your structural equivalent), and
  the eval still prints `PASS exception row parsed on revision 9999999999`.
- `uv run --with pytest pytest -q product/nz_election` all pass; `bin/lint` prints ok lines.
- Commit on the branch; do not push; `last.md` not committed. Final message: what changed in
  five lines, the three command outputs (last lines), anything you chose not to do.
