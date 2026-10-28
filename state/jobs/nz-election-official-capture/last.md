Committed `d97ac35`; not pushed.

Changed `tools/official_capture.py`, `pipeline/fetch.py`, `tests/test_official_capture.py`, and the settled/official runbook section. Added serial acquisition, provenance, preflight and review instructions.

Required verification:

```sh
uv run --with pytest pytest -q product/nz_election/tests/test_official_capture.py product/nz_election/tests/test_result_import.py product/nz_election/tests/test_result_states.py product/nz_election/tests/test_settlement_capture.py
```

```text
1 failed, 128 passed in 292.26s (0:04:52)
```

The unchanged browser test failed because the sandbox denied Chromium’s macOS MachPort registration. No tests were changed or skipped.

Final new test file:

```text
40 passed in 54.70s
```

`bin/lint`:

```text
lint ok (1380 text files)
```

`last.md` remains uncommitted with the command, PASS line and verification details. Remaining: rerun the full suite where Chromium can launch; confirm the official EC endpoint when published.