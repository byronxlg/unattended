# nz-election-6: Mangere capture landed, align the two tests that assumed it was missing

You are on the increment 6 build thread in .worktrees/nz-election-6 (branch change/nz-election-6).
The supervisor has committed the last 2023 capture, ec-2023/candidate-votes-by-voting-place-21.csv
(Māngere, N=21), with its manifest entry; the manifest now has 111 entries and all 72 voting-place
files exist. Host run on that commit: `verify.py all` PASS (candidates 71, electorates 71 pages),
daily_refresh PASS, build 77 routes, lint ok, pytest 342 passed, 2 failed. Both failures are
assumptions in tests that file 21 was absent, not product defects:

1. product/nz_election/tests/test_contracts.py::test_capture_manifest asserts `len(captures()) == 110`.
   The manifest has 111 entries now. Update the count (and any other place that pins 110 or
   "71 of 72" captures).
2. product/nz_election/tests/test_contracts.py::test_baseline_source_set_advancement[add] appends a
   synthetic source whose id is `ec-2023/candidate-votes-by-voting-place-21.csv`; that id is now a
   real source in the envelope, so the "add" case no longer adds a key and publish keeps the
   previously published data. Use a synthetic id that cannot collide with a real capture (for
   example a clearly fake `ec-2023/candidate-votes-by-voting-place-99.csv`, or a wikipedia source id
   that is not in the envelope) so the test still proves source additions advance published data.
   Do not change publish.py or the drop and add-regressed cases.

Read first: the two tests above, product/nz_election/pipeline/fixtures.py (captures), and
state/jobs/nz-election-6-fix/last.md if you need the fix context. Grep tests and pipeline for
`110`, `71 of 72`, `voting-place-21` and `Māngere`/`Mangere` to catch every remaining
"file 21 is missing" assumption; test_verifier_accepts_present_mangere and the controlled-missing
checks from the fix stay as they are. Only tests and test fixtures may change; no pipeline or web
code. Commit on the branch; do not push.

Definition of done, run in the worktree and paste the tail of each:
- `uv run --with pytest pytest -q` expected `344 passed` (0 failed)
- `uv run product/nz_election/pipeline/verify.py all` expected ending `PASS all`
- `bin/lint` from the repo root expected `lint ok`
Report: commit sha, files changed, what each changed assertion now proves, and the outputs.
