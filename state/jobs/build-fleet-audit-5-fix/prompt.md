# Fix: Fleet Audit increment 5, fresh review findings

Same worktree `.worktrees/fleet-audit-5`, branch `change/fleet-audit-5`, HEAD e6e4600. Commit in
the worktree; never push. Existing tests and fixtures stay as they are; you may add new test
functions to `tests/test_reports.py` for the two findings below, nothing else under `tests/`.
`tests/conftest.py` unchanged.

## Important 1: scan drops plist field errors from uncertainties (scan.py scan_fleet)

`scan_fleet` builds `uncertainties` only from `obs.error`, so a plist that parsed but carries
`field_errors` (for example `StandardOutPath` set to an integer) contributes nothing. Rule 6
(running) then returns before rule 9 ever sees the field errors (verdicts.py line 104 is the
only place that reads them), and the job reports `running`, uncertainties `[]`, exit 0. The
spec's exit 2 clause says ancillary errors on running jobs are unresolved uncertainty; exit 0
requires no uncertainty. In audit this cannot happen because `join_plists` exits 3 on field
errors; scan has no such gate. Fix: include each plist field error in the job's uncertainties
(the `'{name}: {message}'` shape already used) before `evaluate`, so the summary's
`uncertainties` count is nonzero and `exit_code` yields 2 for an otherwise running job. Keep
the verdict `running` (process presence stands); do not change rule order. Add a test
`test_scan_plist_field_errors_are_uncertain` that takes an existing fleet snapshot, injects a
plist with an invalid `StandardOutPath` through a `SnapshotFiles` subclass the way
`test_reports_never_emit_environment_values` does, and asserts the uncertainty is present and
the exit code is 2.

## Important 2: receipt timestamp normalisation can raise OverflowError (receipts.py timestamp)

`timestamp()` now calls `parsed.astimezone(timezone.utc)`; for `0001-01-01T00:00:00+01:00`
that raises `OverflowError: date value out of range`, which nothing catches (reproduced with
`normalize_tick`). A receipt must never crash the audit; an unparseable timestamp is an
uncertainty. Fix: catch `OverflowError` with `ValueError` and return None (invalid timestamp),
same as the existing branch. Add a test `test_receipt_timestamp_overflow_is_invalid` asserting
`normalize_tick` with that `ts` returns a record whose `ts` is None (or whatever the existing
invalid-timestamp path yields; match it, do not invent a new shape).

## Definition of done

From `product/fleet_audit/`: the five acceptance stages (`registry`, `observer`, `verdicts`,
`drift`, `fleet`, each `uv run python -m fleet_audit.acceptance <stage> --offline`, last line
`OK <stage>`), `uv run --with pytest pytest -q` (zero failures, 313 or more tests). From the
worktree root: `bin/lint` exit 0; `rg -l '^(import|from) subprocess'
product/fleet_audit/fleet_audit` prints only `collect.py`. Final message under 20 lines:
commit hash, the outputs, anything you could not do.
