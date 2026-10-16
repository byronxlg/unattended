Committed `7dca242`; not pushed. Added Python/JS coalition logic, hash validation, script allowlist, controls, parity tests and browser checks. Updated build, verifier, polls template, CSS and screenshot harness. Enforcers documented in [coalitions.md](product/nz_election/coalitions.md).

```text
uv run --with pytest pytest -q
252 passed in 31.01s
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
Offline verification: immutable captures, not live data
PASS refresh: polls bundle
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election
PASS build: 6 routes
uv run product/nz_election/pipeline/verify.py coalitions
PASS coalitions
uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS all
printf '%s' '[{"op":"decode","hash":null,"parties":[]}]' | node product/nz_election/tests/coalitions_runner.mjs
[{"error":"INVALID_COALITION_STATE"}]
bin/lint
lint ok (234 text files)
```

Added **12 tests**, including byte-equal scenario parity. Screenshot contract: **12 baseline + 12 state images = 24**.

Departures:

- Missing `plan-m2.md`: followed brief and spec.
- Deliberately replaced M1 script prohibitions, including screenshot checks; injection tests unchanged.
- Vacancy screenshot shows unchecked-capacity uncertainty; real-candidate vacancy arithmetic is tested separately.

Both browser commands hit Chromium’s sandbox permission restriction. Screenshots remain uninspected; supervisor must run:

```sh
uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site site
uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots
```