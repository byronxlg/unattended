# Follow-up 1: the test contracts move with the route and the family

You stopped correctly. The brief's line "do not edit existing tests" was mine and it was wrong for
this change: the existing tests encode the registered route set and family set, and a change that
adds a route and a family has to move those contracts in the same commit. That is a build, not a
fix, so it is allowed here. The rule that still binds: nothing gets weaker. Every assertion keeps
checking the same invariant for the larger set.

Do, in this worktree, on the same branch, new commits (not amended):

1. Route count. The invariant is "every registered route in `config/routes.json` is built exactly
   once and screenshotted". Replace the literal 77 in `tests/test_build.py`,
   `tests/test_geography.py` (check whether that 77 is routes or electorates; electorates stay),
   `tests/test_design.py`, `tests/test_electorates.py` and `tests/screenshots.py` (the assert and
   the PASS line) with the new count derived from the same source the build reads, or the literal
   78 if the other tests use literals; keep the uniqueness assertion.
2. Family union in `tests/test_contracts.py::test_hourly_daily_race_preserves_union`. The invariant
   is "after the workflows that own them have published, every registered family's files are on
   the data branch and `status` lists every family". `social` is published by its own daily
   workflow, so either the test publishes all three families (the race between hourly and daily
   stays; social can run after) or `export.py` distinguishes the families the hourly/daily pair
   owns from `social` and the test asserts the union over the right set, with `status` still
   listing `social` (absent is a valid status). Pick the one that keeps `publish.py` honest about
   what each workflow owns and say which you chose in `last.md`.
3. Your own `test_build_present_absent_stale_no_identifiers` raises `UNSAFE_OUTPUT_PATH` from
   `build.py:423`: fix the test's output path to what `build.py` requires (read that check first).
4. Run the definition of done from the original brief again and paste the final output of each
   command. `verify.py all`: add the social check the brief asked for if it is missing, or say in
   `last.md` why `verify.py` cannot see the family.

Unchanged: no live Jev or X requests, no identifiers anywhere, no edits to any assertion that is
not about the route count or the family set. If anything else in the existing tests blocks you,
stop again and name the test and the line.
