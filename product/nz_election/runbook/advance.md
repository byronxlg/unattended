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
counts do not establish cumulative semantics. Ambiguous columns fail
`INVALID_ADVANCE`; investigate the source and adapt the detector in reviewed code,
without rewriting raw bytes. Malformed files also fail `INVALID_ADVANCE`.

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
