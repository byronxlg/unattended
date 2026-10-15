# Follow-up: Fleet Audit increment 1, two review findings

Same worktree `.worktrees/fleet-audit-1`, branch `change/fleet-audit-1`, on top of your commit
e2f9e54. Supervisor review of increment 1: tests, acceptance, lint and the CLI demo all passed
when run by the supervisor. Two findings to fix, nothing else. Commit in the worktree; never push.

## 1. Unhandled RecursionError in plist parsing (Important)

`fleet_audit/plists.py` `observe_plist` catches ValueError, TypeError, OverflowError, ExpatError
and InvalidFileException, but `plistlib.loads` can also raise `RecursionError` (a binary plist
whose container references itself; Python documents RecursionError as a possible outcome of
loading malformed binary plists). Today that escapes `declared` as a traceback instead of
exit 3 with `invalid plist: RecursionError: malformed plist`. `parse_frontmatter` already
catches RecursionError; make the plist path consistent.

- Add `RecursionError` to the except tuple in `observe_plist`.
- Add a test in `tests/test_plists.py` (or `test_plist_join_errors`) that feeds a self-referencing
  binary plist through `join_plists` with a fake file source and asserts the declared error
  message ends with `invalid plist: RecursionError: malformed plist`. Build the bytes in the
  test (a minimal bplist00 whose single object is an array whose only element is object ref 0);
  do not add a binary fixture file. If a self-reference does not produce RecursionError on
  Python 3.12 (check by running it), say so in your final message and instead assert via
  monkeypatching `plistlib.loads` to raise RecursionError; either way the except tuple change
  stays.

## 2. Repository-level pytest now fails at collection (Important)

From the worktree root, `uv run --with pytest pytest -q` (the command `CLAUDE.md` names, and
what the CI Tests step runs once a root test exists) now collects `product/fleet_audit/tests`
under the host's Python 3.11 with no package installed and errors with
`ModuleNotFoundError: No module named 'fleet_audit'`. The package tests must only run from
`product/fleet_audit` (Python 3.12, its own venv), which the new CI step already does.

- You may create one file outside the package for this: `pytest.ini` at the repository root
  (the worktree root), content:

  ```
  [pytest]
  norecursedirs = .* product
  ```

  Nothing else outside `product/fleet_audit/`. Do not touch `.github/workflows/ci.yml` again.

## Definition of done

Paste actual output of each:

1. From the worktree root: `uv run --with pytest pytest -q` prints `no tests ran` and does not
   error at collection (exit code 5 is expected and fine; say what the exit code was).
2. From `product/fleet_audit/`: `uv run --with pytest pytest -q` with zero failures and the
   test count (expected 192 or more).
3. From `product/fleet_audit/`: `uv run python -m fleet_audit.acceptance registry --offline`
   last line `OK registry`.
4. From the worktree root: `bin/lint` exits 0.

Final message under 25 lines: files changed, the four outputs, and anything you could not do.
