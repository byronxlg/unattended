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

## Increment 1 departures

The worktree starts at af1b585. Read the accepted plan from local commit 62d3ff6;
the plan and tests/test_ci.py are absent in this checkout. Existing tests stay unchanged.
The brief forbids every fixture edit, including new files. Generate golden inputs in
memory from checked captures; synthetic parser and allocator cases live in tests.
No allocator-golden.json or parser-cases.json is written under fixtures.
The pinned Verian 8-11 August poll sorts as 12 August. A revision-specific exception
uses visible fieldwork dates and reports the disagreement in diagnostics.
Names differ between CSV and XML; join by structural IDs, not names or similarity.
