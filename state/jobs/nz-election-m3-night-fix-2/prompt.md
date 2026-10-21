Follow-up on PR #59 (second fresh review request changes, two Important, one nit). Same worktree, same branch,
commit on top of the current head (6e1547b), do not push. No page code, no templates.

1. pipeline/night.py:86: "Final snapshot" is inferred from the absence of derivation metadata. Strip `derivation`
   and `elapsed_seconds` from the illustrative step 0, copy the archive timestamp, relabel row and sequence "Final
   snapshot", and prepare() plus validate() accept 285,114 synthetic votes as final results. The invariant: a row
   labelled as an archive or final snapshot must match its source capture (votes and hash of the archived XML it
   claims to come from), checked independently of any removable metadata. Enforce it in validate() and add a test
   that performs exactly that strip-and-relabel and expects rejection.
2. pipeline/xml_parser.py:109: electorate seats are not bounded against the reference registry. One 2023 party with
   candidate_seats 999 and total_seats adjusted passes and returns House 1119 with 72 electorates. Reject with
   XML_TOTAL when summed electorate seats exceed the registry's electorate count (and any per-party electorate seat
   count above it); add the test.
3. Nit: pipeline/verify.py:355: `--data` on an empty directory raises INVALID_INVENTORY as a traceback before the
   night-family check. Report it as a named failure line (no traceback, nonzero exit), or make the runbook say so.

Tests on origin/main stay as they are; this branch's own tests may move. Done when
`uv run --with pytest pytest -q product` passes, the night verify command prints PASS night, the new tests fail on
6e1547b, and `bin/lint` prints lint ok; report the counts and do not commit last.md.
