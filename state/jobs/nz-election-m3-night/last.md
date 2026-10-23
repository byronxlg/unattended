Committed `520b7e6`; not pushed.

Added XML validation, labelled archives/demo/replay, atomic night-family publication, CSV exports, runbook and tests. No page, static or screenshot changes.

Verification:
- `uv run --with pytest pytest -q product`: `1489 passed in 402.43s`
- `verify.py night`: `PASS night`
- `verify.py all --data /tmp/nz-night-populated`: `PASS all`
- Smoke: `2851211 valid party votes; House 122`
- `bin/lint`: `lint ok (588 text files)`

`last.md` remains uncommitted with full results and deferred page/client tests. Electorate detail remains absent; source-local timestamps remain unconverted.