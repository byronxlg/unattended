Committed `15a30be`; not pushed. Working tree clean.

Changed only `product/nz_election/tests/test_contracts.py`:
- Manifest assertion now requires 111 hash-validated captures.
- Source-addition test uses synthetic file 99 and asserts its ID is absent before publishing.
- Drop, add-regressed and controlled-missing checks remain unchanged.

Verification tails:
```text
uv run --with pytest pytest -q
344 passed in 85.02s (0:01:25)

uv run product/nz_election/pipeline/verify.py all
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS all

bin/lint
lint ok (281 text files)
```