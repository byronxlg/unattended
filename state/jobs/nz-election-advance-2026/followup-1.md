# Follow-up 1: nz-election-advance-2026

Your 4ae0d41 is right to commit a real 2026 capture; that moves one contract. Authorized: the first
assertion of `test_require_year_missing_and_registered_invalid` (product/nz_election/tests/test_advance.py:206-207,
MISSING_ADVANCE_CAPTURE) may change so that it runs against an empty registered 2026 set (monkeypatch the
registry, the same way `register_2026` does, with no files) instead of the repo's real registry. The invariant
stays: with no registered 2026 capture, `verify advance --require-year 2026` fails MISSING_ADVANCE_CAPTURE.
Nothing else in tests on main at d6acf2c moves. Add one test that `verify advance --require-year 2026` passes
on the committed capture.

Done when, in the worktree:
- `uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home"` shows only the
  Chromium sandbox-launch denials as failures (name them); the host runs those.
- `bin/lint` prints `lint ok`.
Commit; do not push; do not commit last.md.
