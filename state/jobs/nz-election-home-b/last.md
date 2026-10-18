Committed `748fc5f` on `change/nz-election-home-b`. Not pushed.

Changed night copy/countdown, candidates-first details, shared metadata, 79 OG documents, PNG generation, `home-routes`, deployment checks and runbook.

Files changed under `product/nz_election/`:
- Pipeline: `build.py`, `electorate_pages.py`, `route_cards.py`, `route_checks.py`, `verify.py`.
- Web: `styles.css`; templates `base.html`, `electorate.html`, `night.html`, `og.html`.
- Tests: `screenshots.py`, `test_home.py`, `test_home_routes.py`; plus `runbook.md`.
- Also `.github/workflows/pages.yml` and `intent/nz-election/plan-home.md`.

Pins moved:
- `tests/screenshots.py:410`: 219 → 296 images.
- `tests/test_home.py:202`: 219 → 296.
- `tests/screenshots.py:257,261`: two OG specimens → all 79 routes.
- `runbook.md:248`: 219 → 296; derived as 158 + 9 + 33 + 13 + 4 + 79.

`pages.yml`: after verification, install Chromium only; run `--og-only`; require referenced PNGs and 1200×630 dimensions; continue blog build/upload. Existing freeze guards and ordering unchanged.

Actual verification:
```text
uv run product/nz_election/pipeline/verify.py home-routes
PASS home-routes
uv run product/nz_election/pipeline/verify.py all
PASS all
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election --now 2026-10-17T01:00:00Z
PASS build: 79 routes
uv run --with pytest pytest -q product/nz_election
567 passed in 242.06s (0:04:02)
uv run --with pytest pytest -q
651 passed in 240.53s (0:04:00)
bin/lint
lint ok (447 text files)
```

Host commands, with expected outputs:
- `uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots` → `PASS screenshots: 79 routes, 296 images`
- `uv run product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/og --og-only` → `PASS screenshots: 0 routes, 79 images`
- `uv run product/nz_election/tests/coalitions_browser.py --site site` → `PASS coalition browser`

Verification departure: OG-only launch failed `CHROMIUM_REQUIRED` with macOS Mach-port permission denied. Visual inspection, fold measurements and Pages-run evidence remain pending; checks were not weakened. Generated `artifacts/` remains untracked.