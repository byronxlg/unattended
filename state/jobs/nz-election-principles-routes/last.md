Committed `0bfcaff`; not pushed.

Opened prose/source disclosures, preserved fragment IDs and source links, and added the table-only disclosure check.

Verification:

- `uv run --with pytest pytest -q product`: `638 passed`
- `uv run python -m product.nz_election.pipeline.verify all`: `PASS all`
- `bin/lint`: `lint ok (479 text files)`
- New check fails on c6d8ff3 and passes on HEAD.

Details and disclosure counts are in uncommitted [last.md](last.md).

Outstanding: screenshots. Chromium launch failed with sandbox permission denied; visual verification remains incomplete.