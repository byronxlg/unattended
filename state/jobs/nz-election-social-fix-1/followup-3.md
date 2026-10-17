# Follow-up 3: the 490 headroom pin is this branch's own test; move it, restore "New Zealand First"

The conflict you reported is a brief error, not a protected check. `test_hourly_queries_fit_with_headroom`
in `test_social_diagnostics.py` was added by this branch in bc917a6 (`git log --oneline --
product/nz_election/tests/test_social_diagnostics.py` shows only bc917a6 and e22221e). "Pre-existing"
in follow-up 2 meant tests that are on `main` (79af3d6); nothing on `main` pins the phrase list or the
490 number. Tests this branch introduced are yours to adjust; tests on `main` stay untouched.

Do both items of follow-up 2 as written, with this change:

- The invariant is: every fully composed query (base phrases plus the hourly window suffix, exactly as
  sent) stays within the upstream limit for every date the windows can produce, and the runtime guard
  from item 1 enforces that limit at one named constant. Rewrite the headroom assertion against that
  constant rather than a magic number, keeping some stated headroom (your choice of margin; say why in
  the test's docstring or a comment). With "New Zealand First" restored you measured 495 to 499
  characters, so the margin must admit 499 and reject 513.
- Item 1 (guard, `SOCIAL_QUERY_TOO_LONG`, boundary tests at 512 and 513) unchanged.
- Item 2 caption sentence and `intent/nz-election/social.md` unchanged.

Commit on the branch, do not amend or push. Rewrite `last.md` with the exact outputs of:
`uv run --with pytest pytest -q product/nz_election/tests` (all passed),
`evals/social-query-length/check.sh` (PASS and the number, expected 499 or under),
`evals/pages-verify-polls-only/check.sh` (PASS all), `bin/lint` (ok). Leave `last.md` uncommitted.
