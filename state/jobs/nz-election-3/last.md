Committed `2ac4067` on `change/nz-election-3`. Not pushed; working tree clean.

Changed both workflows; pipeline `fetch.py`, `refresh.py`, `publish.py`, `build.py`; product AGENTS/runbook; three test files. No template or style changes.

Verification ran offline (`UV_OFFLINE=1`):

1. `uv run --with pytest pytest -q product/nz_election/tests/test_workflows.py`
   `4 passed in 3.64s`
2. `uv run --with pytest pytest -q product/nz_election/tests/test_pipeline.py product/nz_election/tests/test_build.py`
   `19 passed in 12.59s`
3. `uv run --with pyyaml python -c "import yaml,sys;[yaml.safe_load(open(p)) for p in sys.argv[1:]];print('yaml ok')" .github/workflows/pages.yml .github/workflows/nz-election-hourly.yml`
   `yaml ok`
4. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   `Offline verification: immutable captures, not live data`
   `PASS refresh: polls bundle`
5. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   `PASS build: 6 routes`
6. `uv run product/nz_election/pipeline/verify.py all`
   `PASS polls`
   `PASS thresholds`
   `PASS provenance`
   `PASS pipeline`
   `PASS all`
7. `uv run --with pytest pytest -q`
   `240 passed in 27.89s` (0 skipped)
8. `bin/lint`
   `lint ok (223 text files)`
9. `git status --short`
   No output after commit.

First live run: resolve absent data ref; skip snapshot checkout; fetch and validate Wikipedia; upload the validated bundle or unavailable status; publication validates again and creates the orphan data commit. Handled failure then fails the workflow. Pages accepts completion regardless of conclusion, resolves/checks out the data SHA, builds, records actual SHAs, and deploys.

Departures: retained the existing leased-push rule; used validated status.json as the typed result record. Added all four planned workflow tests, three pipeline tests and one build test for fetch safety, provenance, artifact gating and checkout metadata.

Open questions: none. Supervisor still needs screenshots and the first live Actions/deployment verification.