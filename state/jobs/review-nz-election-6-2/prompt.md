Fresh-context review of the fix and test-alignment commits on branch change/nz-election-6 (NZ
election increment 6). Worktree .worktrees/nz-election-6, read-only. Follow REVIEW.md. Important
or Nit, at most five nits, nothing bin/lint reports. Do not approve.

Scope: `git diff 7241c10..HEAD -- product ':!product/nz_election/fixtures'` (6 files, about 136
insertions, 22 deletions). 7241c10 is the build commit already reviewed (review-nz-election-6
found three Important items). f787d3e is the fix; 0719555 adds the Māngere 2023 capture (file 21,
now present, manifest 111 entries); 15a30be aligns two tests with the complete baseline set.

The three Important items the fix must close, with the invariant each protects:
1. publish.py keep rule: a bundle that gains sources must publish; a bundle that drops sources, or
   drops one while adding another, must keep the previously published data. Check the subset and
   superset comparison and the add, drop and add-regressed cases in test_contracts.py. Look for a
   path the tests miss (empty previous source set; same ids with changed urls or hashes; ordering).
2. verify.py and test_electorates.py no longer require Māngere specifically to be missing: the
   verifier must use controlled present and missing inputs and the real fixtures now have all 72
   files. Confirm no test or verifier branch still encodes "file 21 absent" as the expected state,
   and that the "no candidate baseline" rendering is still exercised by a controlled-missing case.
3. candidates.py: repeated reviewed claims on one field accumulate without raising, and an agreeing
   supplemental mapping never replaces EC provenance. Find the test for each and a path it misses
   (three claims; a claim that agrees then one that disagrees; claim order).

Then:
4. Test diff discipline: `git diff 7241c10..HEAD --stat -- product/nz_election/tests` and the
   removed lines. The fix (f787d3e) must not remove or weaken an existing assertion; 15a30be may
   change exactly two assertions (manifest count 110 to 111; add case synthetic id 21 to 99). Report
   any other removed or loosened line.
5. Sandbox run if the read-only sandbox allows: `uv run --with pytest pytest -q` (expected: 344
   passed, 0 failed) and `uv run product/nz_election/pipeline/verify.py all` (expected PASS all).
   Say what you could not run.

Report: the diff you read, each check with its evidence (file:line, commands and output), Important
findings with a reproduction, nits, and "Important findings: N" as the last line.
