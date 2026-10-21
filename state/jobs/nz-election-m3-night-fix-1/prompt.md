Follow-up on PR #59 (fresh review request changes, four Important). Same worktree, same branch, commit on top of
the current head, do not push. No page code, no templates.

1. pipeline/night.py:160: mode validation checks that row and sequence labels agree, not where the data came from.
   One demo observation relabelled `Final snapshot` on both row and sequence passes prepare() and validate(), so
   simulated results could publish without the demo label. Bind the permitted modes to the source or derivation
   provenance (a demo/replay source can only carry the demo mode), and add a test that relabels a demo observation
   and expects rejection.
2. pipeline/xml_parser.py:110: percentage validation is skipped when summed votes are zero. All party votes zero
   with nonzero percentages and seats is accepted (valid votes 0, House 122). Reject it with XML_TOTAL; add the test.
3. pipeline/verify.py:331: night verification builds fresh fixtures instead of checking the supplied artifact, so a
   `--data` bundle with no night family gets PASS night. Run the night smoke checks against the supplied data when
   --data is given (a missing night family fails with a named code); keep the fixture path for the no-data case. Test
   both.
4. pipeline/xml_parser.py:44: empty or whitespace-only count elements (`<votes/>`, `<votes> </votes>`) fail as
   XML_FIELDS while other malformed counts fail as XML_COUNT, against the documented contract. Make them XML_COUNT and
   test through the XML parse path, not count() directly.

Tests on main at the base sha (605b316 line, i.e. what is on origin/main) stay as they are; this branch's own tests
may move. Done when `uv run --with pytest pytest -q product` passes, `uv run python -m product.nz_election.pipeline.verify night`
(or the existing night verify command the runbook names) prints PASS night, and `bin/lint` prints lint ok; report the
counts and do not commit last.md.
