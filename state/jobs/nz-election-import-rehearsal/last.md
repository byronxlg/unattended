Committed `a751c4d`; not pushed.

Added the isolated workflow job, rehearsal entry point, synthetic adapters, three tests and runbook instructions. `last.md` remains uncommitted with dispatch instructions and expected PASS lines.

Verification:

```sh
uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py product/nz_election/tests/test_settlement_capture.py product/nz_election/tests/test_result_states.py product/nz_election/tests/test_workflows.py product/nz_election/tests/test_night_rehearsal_contract.py
```

```text
1 failed, 117 passed in 246.73s
```

The unchanged browser test failed because macOS denied Chromium’s Mach port registration. Full acceptance remains blocked.

```text
New rehearsal tests: 3 passed in 43.82s
bin/lint: lint ok (1364 text files)
```

After merge:

```sh
gh workflow run nz-election-night-rehearsal.yml --ref main -f import_only=true
```

The rehearsal uses a recorded offline scenario timestamp; production clock and guard constants remain unchanged.