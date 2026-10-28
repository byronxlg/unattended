Committed `80235df`; not pushed.

- Shared totals and rounding in `funding_page.py` / `home_graphics.py`.
- Added data parity test in `test_funding_totals.py`.
- Updated `test_design.py` with structural landmarks and missing/duplicate cases.
- No existing rounding assertions changed.

`funding_bars()` rounding deltas: ACT -$0.40, National -$0.20, Labour -$0.08, NZ First +$0.02, Green +$0.44. Others unchanged. Current published home/funding totals unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "funding or design or home_graphics"
5 failed, 81 passed, 3053 deselected in 89.46s (0:01:29)

bin/lint
lint ok (1348 text files)
```

All five failures are Chromium launch permission errors from the sandbox. New regression cases pass. Browser verification and screenshots remain blocked; details in uncommitted `last.md`.