Committed `131115b`, not pushed.

- Updated `build.py` and `market_panel.py`: sunset wording, retained observation dates, separate failure lines.
- Added renderer tests in `test_polls_plan.py` and `test_markets.py`. No protected assertions changed.
- New tests against origin/main: **18 failed, 18 passed**.

Verification:
```sh
uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_polls_plan.py product/nz_election/tests/test_markets.py product/nz_election/tests/test_home_failed.py
```
```text
161 passed in 30.50s
```

`bin/lint`:
```text
lint ok (1458 text files)
```

Populated healthy/failed builds and provenance checks passed.

Remaining limitation: screenshots blocked by Chromium’s macOS sandbox permission error. Details recorded in uncommitted `last.md`.