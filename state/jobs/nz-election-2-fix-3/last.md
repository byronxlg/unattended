Committed `61d405e`; not pushed.

Updated export validation, refresh/build producers, publication ordering and runbook. Operational timestamps require `YYYY-MM-DDTHH:MM:SSZ`; invalid forms raise `INVALID_TIMESTAMP`. Date-only fields stay date-only. Publication uses canonical string ordering.

Added 23 regressions in `test_timestamp_canon.py`: fractional failed attempts cannot publish, naive generation timestamps fail validation, producers reject invalid timestamps, and Auckland rendering is identical under both host timezones. Existing tests unchanged.

Commands ran with `UV_OFFLINE=1`:

1. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   `Offline verification: immutable captures, not live data`; `PASS refresh: polls bundle`
2. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`
   `PASS build: 6 routes`
3. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   `PASS build: 6 routes`
4. `uv run product/nz_election/pipeline/verify.py all`
   `PASS polls`; `PASS thresholds`; `PASS provenance`; `PASS pipeline`; `PASS all`
5. `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
   `CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed`
   Chromium: `bootstrap_check_in ... Permission denied (1100)`
6. `uv run --with pytest pytest -q`
   `232 passed in 23.43s`
7. `bin/lint` after staging: `lint ok (198 text files)`
8. `git status --short` after commit: empty.

Departures: no fresh screenshots could be produced or inspected; supervisor host run required. Open questions: none.