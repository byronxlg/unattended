Committed `78a9b94`. Not pushed.

- `coalitions_browser.py`: corrected synthetic data URLs. Envelope and all assertions preserved.
- `coalitions.mjs`: restored “Seats are unavailable”.
- `last.md`: cause, fix, commands and outputs; left uncommitted.

Verification:

```text
uv run product/nz_election/pipeline/build.py --data /tmp/nz-coalitions-fix/data --out /tmp/nz-coalitions-fix/site/nz-election --now 2026-10-17T01:00:00Z
PASS build: 81 routes

uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site /tmp/nz-coalitions-fix/site
CHROMIUM_REQUIRED: Chromium launch permission denied (1100)

uv run --with pytest pytest -q product
1 failed, 2017 passed, 2 errors in 574.71s (0:09:34)

bin/lint
lint ok (829 text files)
```

All three pytest failures/errors are Chromium launch denials. Coalition unit tests: 14 passed. Node client probe: both synthetic transitions passed.

Outstanding: host browser run and screenshots.