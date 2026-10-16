Committed `0e82e89` on `change/nz-election-2`; not pushed.

Changed product pipeline, exports, templates/styles, route configuration, tests and runbook. Added only the no-data build step to `pages.yml`. Fixtures and existing tests remain unchanged.

Commands ran with `UV_OFFLINE=1`:

1. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   Output: `Offline verification: immutable captures, not live data`
   Output: `PASS refresh: polls bundle`
2. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election`
   Output: `PASS build: 6 routes`
3. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   Output: `PASS build: 6 routes`
4. `uv run product/nz_election/pipeline/verify.py all`
   Output:
   ```text
   PASS polls
   PASS thresholds
   PASS provenance
   PASS pipeline
   PASS all
   ```
5. `uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`
   Error: `CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed`
   Cause: `bootstrap_check_in ... Permission denied (1100)`.
6. `uv run --with pytest pytest -q`
   Output: `199 passed in 12.39s` (0 skipped).
7. `bin/lint`
   Output: `lint ok (195 text files)`
8. `git status --short`
   Output: empty after commit. Generated outputs are ignored.

Added 28 tests: averages 8, contracts 5, pipeline 9, build 6. HTTP retries remain deferred; local publication safety, correction history and primitive parity receive coverage.

The fixture window lacks Others coverage, so seats are withheld. Earlier coherent-window screenshots are separately labelled. No images could be inspected; no screenshot-driven changes are claimed. Code review moved narrow-segment counts into label lanes.

Supervisor follow-up: run screenshots on the host and review all baseline and additional-state images.