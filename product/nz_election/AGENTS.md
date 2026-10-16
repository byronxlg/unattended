# NZ election core

Builds and tests are offline. Runtime Python uses only the standard library.
Keep captures immutable; validate the manifest before parsing any source bytes.
Preserve source URLs, revisions, acquisition times and source-family licences.
Poll-derived data is CC BY-SA 4.0; EC data has no stated open licence.
Use integer/Fraction arithmetic in Python and BigInt in JS. Percentages use Decimal.
Candidate joins use party, list rank and electorate IDs, never name similarity.
Unknown poll structures fail parse_drift; refresh must retain the last-good bundle atomically.
Mappings and exceptions require an explicit source and reason. No silent corrections.
UI increments follow root design rules and require phone and desktop screenshots.

Verification: `uv run --with pytest pytest -q`, `bin/lint` after staging new files.
Node is required for parity, never skip it. Do not add runtime dependencies.

Publish complete validated directories with atomic exchange; never replace files one by one.
Fixture outputs must say offline verification, never live data.
No-data builds retain the official worked example but never substitute fixture polls.
