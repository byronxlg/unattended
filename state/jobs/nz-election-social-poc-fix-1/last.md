Committed **`0642382`**: `Close social privacy, freeze and credit accounting gaps`. Not pushed.

Fixed all six items: closed model registry, build/deployment freeze guards, durable reservation consumption, midnight budget checks, fixed-point probabilities, and figure source references.

Verification:
- **339 tests passed** in 171.39s.
- Eight new regressions failed on `1271c0e` and now pass.
- Existing tests and assertions unchanged.
- Fixture pipeline: **PASS social**, **78 routes**, **PASS all**.
- Lint: **lint ok (348 text files)**.
- Secret-name scan: no unexpected matches.

Evidence and exact commands are in untracked [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-social-poc/last.md).

Chromium remains blocked at sandbox launch. Host must run and inspect populated screenshots:
```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots
```

No live X or Jev requests.