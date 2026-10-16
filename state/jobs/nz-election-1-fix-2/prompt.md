Second fix brief for change/nz-election-1 (PR #9), same worktree. Commit there; never push.
A second fresh review of 3b234f6 found two Important items and one the supervisor calls a nit.

Invariant for both: the allocator contract is one decision per JSON document. Given the same
JSON text, the Python and JS allocators accept or reject identically and return identical
results, including order (spec "Allocator contract"; the parity runner is where this is proved).

1. Important. Integral JSON numbers: with "baseSeats": 1.0 or "partyVotes": {"A": 100.0},
   Python raises INVALID_INPUT and JS allocates. JSON.parse cannot tell 1 from 1.0, so the two
   can only agree if Python treats a finite integral float as that integer (booleans and
   fractional values stay rejected). Decide the rule once, apply it to every numeric field in
   both languages, and add the cases to the parity set.
2. Important. Party ordering: JS sorts ids by UTF-16 code units, Python by code points. Two
   parties "" and "𐀀" (U+10000) with equal votes and one seat put a different
   party first in unresolved ties. Use one comparator (code-point order) in both; add the case
   to the parity set.
3. Nit, fix anyway: poll_parser.py around line 145 matches attribute name prefixes
   case-sensitively although attributes() normalises names, so DATA-SORT-VALUE fails the bundle
   with invalid_dates. Recognise names case-insensitively before normalising; one regression case.

Rules: no edits to existing tests or anything under product/nz_election/fixtures/; add the
regression cases; exact arithmetic stays. No emojis, no em dashes.

Definition of done, from the worktree root, outputs pasted in your final message:
1. `uv run --with pytest pytest -q` expected: all passed, count greater than 146, 0 skipped.
2. `bin/lint` expected: `lint ok (<N> text files)` after `git add`.
3. `git status --short` expected: empty after your commit.
Final message under 25 lines.
