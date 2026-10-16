Committed `5a4d299` on `change/nz-election-4`; not pushed.

In `web/coalitions.mjs`, moved the unchanged `[data-unassigned].textContent` assignment from **line 155 to line 153**, before the no-seats return now at line 154. No other JS changes. Python output remains unchanged; byte-exact parity passes.

Clarified the filename allowlist and PR-reviewed module provenance in `scripts.py` and `coalitions.md`. Added browser regressions and two parity tests; existing assertions remain untouched.

```text
uv run --with pytest pytest -q
254 passed in 30.96s
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
Offline verification: immutable captures, not live data
PASS refresh: polls bundle
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election
PASS build: 6 routes
uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS all
bin/lint
lint ok (236 text files)
git diff 7dca242 --stat -- '*test*'
3 files changed, 89 insertions(+)
```

Browser checks and screenshots remain for the supervisor’s host run; Chromium cannot start in this sandbox.