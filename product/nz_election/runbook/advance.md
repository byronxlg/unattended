# Advance-voting capture and acceptance

From 27 October NZ, capture the published 2026 file manually from the official
Electoral Commission page. Discover its actual download URL there; do not infer
one from the 2023 path. Keep the downloaded bytes unchanged. Record the actual
UTC acquisition time, source revision/update label, source page and any archive
URL used. An HTML challenge is not a capture.

Run the read-only preflight (no network requests or file writes):

```sh
uv run product/nz_election/tools/advance_preflight.py /path/to/capture.csv --url 'https://<observed-official-download-url>'
```

Add `--archive-url 'https://<actual-archive-url>'` if applicable. Output is JSON:
headers, selected columns, inferred kind, CSV row count, usable observation count,
first/last date, gaps from 26 October, SHA-256, and `manifest_entry` with the same
fields as the 2023 entry. Totals and unavailable-count rows are excluded from
observations. Missing dates remain gaps, never zero votes. Cumulative observations
retain their supplied totals across gaps; daily derivations require adjacent dates.

Review the inference against the official source explanation: increasing daily
counts do not establish cumulative semantics. The detector requires explicit
`daily`/`per day` or `cumulative`/`running total`/`to date` header wording.
Generic `Votes`, `Total votes`, and year/election headers are not evidence, even
when their values increase. They fail `INVALID_ADVANCE` with a missing-evidence
message; investigate the source and adapt the detector in reviewed code,
without rewriting raw bytes. Malformed files also fail `INVALID_ADVANCE`. One
shared reader validates the entire CSV before either consumer ignores total rows
or unused columns, including quotes, row widths and duplicate headers.

Copy the raw file to `product/nz_election/fixtures/` plus the printed entry's
`path` (`ec-2026/advance-voting-<hash-prefix>.csv`). Never overwrite old captures.
Copy `manifest_entry` into `product/nz_election/fixtures/manifest.json`'s `entries`.
The tool cannot know acquisition metadata: replace `captured_at: null` with the
recorded UTC timestamp, set the reviewer, revision (null only when none exists),
and notes describing source scope and confirmed daily/cumulative semantics.
Review the URL, archive URL, hash, licence, dates and all five `advance` fields.
Do not register synthetic test fixtures as production captures.

The newest acquisition replaces the whole series. Every registered revision is
hash checked and parsed. A revision with fewer observations than its predecessor
is rejected as `SHORTER_ADVANCE_CAPTURE`, retaining last-good published bytes.
A missing date with the same or greater observation count remains a gap, without
carrying forward the older date. Equal acquisition timestamps are rejected as
`AMBIGUOUS_ADVANCE_CAPTURE`.

## Reviewed shorter correction

A legitimate shorter correction needs a reviewed manifest supersession, not a
newer timestamp alone. Confirm the reduced coverage against an official source
or correction notice; record its URL, the reason, reviewer and UTC review time.
Keep the corrected file at its new immutable path and retain every older file,
SHA-256, acquisition time, URL, revision and licence unchanged.

In the same manifest commit that registers the corrected entry with its normal
`advance` descriptor, move the `advance` descriptor of **every earlier active
entry for that year** into `superseded_advance.descriptor`. Add this object to
each such old entry (example paths and review details must be replaced):

```json
"superseded_advance": {
  "descriptor": {
    "year": 2026,
    "kind": "daily",
    "start": "2026-10-26",
    "date_column": "Date",
    "count_column": "Daily votes"
  },
  "by_path": "ec-2026/advance-voting-<corrected-hash-prefix>.csv",
  "reason": "Official correction withdraws previously included dates: <source URL>",
  "reviewed_by": "<reviewer>",
  "reviewed_at": "<actual UTC review timestamp>"
}
```

Do not leave an `advance` key on those superseded entries. This is an explicit
reviewed reset of the active series history, including any earlier revisions that
would still trigger the shorter-series guard. Append the superseded paths and
correction evidence to the new entry's `notes`. Never delete the old entries or
modify their raw files. Subsequent ordinary captures retain their active history
and the shorter-replacement guard applies again from this corrected baseline.

No loader hook is required: only entries with `advance` participate in selection;
`superseded_advance` is an audit record, not an automatic bypass flag. Review must
check that every `by_path` names the corrected capture and each archived descriptor
matches its original. Run the commands below before approving the supersession.
Revert the manifest change to restore the previous active history if review fails.

Before committing, run:

```sh
uv run --with pytest pytest -q product/nz_election/tests/test_advance.py
uv run product/nz_election/pipeline/verify.py advance --require-year 2026
```

The required-year command must print `PASS advance`. An absent registered capture
fails `MISSING_ADVANCE_CAPTURE`; malformed captures fail validation. The unflagged
`verify.py advance` remains historical offline verification and does not prove
2026 readiness. The required-year check validates registered source bytes, not
whether the deployed site has received them.

Stage only the immutable capture and reviewed manifest, run `bin/lint`, review the
diff, and commit. Rerun the required-year command after committing and retain its
output in the handoff. Publication uses the existing daily GitHub Actions workflow.
