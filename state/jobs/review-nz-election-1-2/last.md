1. **Important** - `product/nz_election/pipeline/poll_parser.py:145`: Cell attribute detection remains case-sensitive, despite `attributes()` normalizing names. Valid uppercase attributes cause the entire poll bundle to fail.
   Reproduction: change the regression row’s `data-sort-value` to `DATA-SORT-VALUE`; parsing raises `invalid_dates` with the attribute text included.
   Fix: recognize attribute prefixes case-insensitively before passing them to `attributes()`.

2. **Important** - `product/nz_election/pipeline/allocator.py:10`: Integral JSON numbers still produce different validation outcomes.
   Reproduction: use the regression `valid()` input with `"baseSeats": 1.0` or `"partyVotes": {"A": 100.0}`. Python raises `INVALID_INPUT`; JS returns a one-seat allocation.
   Fix: normalize finite, safe, integral Python floats to integers while continuing to reject booleans and fractional values.

3. **Important** - `product/nz_election/web/allocator.mjs:37`: JS sorts party IDs by UTF-16 units; Python sorts by Unicode code points, violating full-result parity.
   Reproduction: two parties `"\ue000"` and `"\u10000"` (the latter expressed in JSON as `"\ud800\udc00"`), each with 100 votes, one candidate, zero electorate wins, and `baseSeats: 1`. Python’s unresolved candidates list starts with U+E000; JS’s starts with U+10000.
   Fix: use the same Unicode code-point comparator in both implementations.

Verification: `uv run --with pytest pytest -q` failed with `Failed to initialize cache ... Operation not permitted`. Python/Node reproductions confirmed all 23 added invalid cases agree, special IDs survive, all 43 pinned poll IDs remain identical, and the official House 122 result and 120 quotients agree. Existing tests were unchanged. No additional security findings.

Important findings: 3