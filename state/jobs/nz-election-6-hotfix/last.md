Committed `84314c4` on `change/nz-election-6-hotfix`. Not pushed; worktree clean.

`verify.py` now checks candidate coverage and 72 baselines independently when their families are present. Bundle validation remains unchanged. Added nine regression tests in `test_verify_supplied.py`; no existing tests, copy, or workflows changed.

Diff stat: **2 files, 67 insertions, 4 deletions**.

Verification commands and tails:

```text
uv run --with pytest pytest -q product/nz_election/tests
269 passed in 117.86s (0:01:57)

uv run product/nz_election/pipeline/verify.py all
PASS all

uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/polls-only &&
uv run product/nz_election/pipeline/build.py --data /tmp/polls-only --out /tmp/site-po &&
uv run product/nz_election/pipeline/verify.py all --data /tmp/polls-only --site /tmp/site-po
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (295 text files)
```

Count clarification: 344 was repository-wide. Product tests total 269 with additions; the separate tooling suite reported `84 passed in 1.40s`, giving **353 passed, 0 failed**.

Used `--fixtures` for offline refresh; live mode requires GitHub Actions environment variables. No sandbox blockers. Open questions: none.