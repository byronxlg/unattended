# Follow-up 1: the six tests move with the invariant (supervisor brief conflict)

You were right to stop. My brief asked for a bounded release-date rule AND for the exception tests
on main to stay true; those six assert that the August Verian row (sort one day after fieldwork end)
fails when its hand entry is altered or removed, which the new rule deliberately accepts. That is
my error. The contract moves; you are authorized to edit exactly these tests on main:

- test_date_exception_revision.py::test_exception_requires_documented_exact_row (5 params)
- test_date_exception_revision.py::test_public_drift_has_only_structural_locator, the 'incident'
  case (date_exceptions emptied)

Rewrite them against the new invariant, nothing weaker:

1. A non-matching or removed exception now parses that row through the release-date rule: assert
   the row parses with fieldwork 2026-08-08 to 2026-08-11 and the substitution appears in the
   diagnostics with its kind (release-date, not the documented exception).
2. Keep a failing case for each: move the wikitext sort value outside the bound (end + bound + 1
   days) or before fieldwork start, and assert ParseDrift invalid_dates with the same structural
   public locator shape ('<visible> / <sort>').
3. The 'incident' locator case keeps pinning public_locator: drive it with an out-of-bound sort.

Every other test on main at 57063db stays as is. Then the definition of done in prompt.md:
both evals PASS, live-file parse (rows and the Freshwater 2026-10-19 row), full pytest all pass,
bin/lint ok. Commit; last.md not committed. Report the rewritten assertions in a short list.
