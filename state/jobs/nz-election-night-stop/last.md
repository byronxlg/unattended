Committed `0a45eab`; not pushed.

Added shared cutoff guards, bundle stop fields, client polling termination, tests, and the runbook’s “Stop” section. Constant: `CLOSE` in `product/nz_election/pipeline/night_live.py:25`.

Verification:

- Requested targeted pytest command: `67 passed in 48.49s`
- `uv run --with pytest pytest -q`: `5 failed, 2511 passed, 2 errors in 656.39s`
- `uv run product/nz_election/pipeline/verify.py night`: `PASS night`
- `bin/lint`: `lint ok (948 text files)`
- `bash -n bin/tick`: exit 0, no output

All seven failures/errors were Chromium launch permission failures: deployed browser checks `[probe/rehearse/faults]`, party-picker layout, result-states browser, XML browser parity, and replay network checks. Screenshots remain blocked.

Full report: [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-night-stop/last.md), left uncommitted.