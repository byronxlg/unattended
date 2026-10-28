Committed `a971810`; not pushed.

- `settlement_capture.py` now scans provenance only. Known-synthetic XML comparison unchanged.
- Added a `DemocracyNZ` regression test, confirmed failing before the fix.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py
50 passed in 202.35s (0:03:22)

bin/lint
lint ok (1298 text files)
```

No Chromium denials. Results recorded in uncommitted `last.md`. No open questions.