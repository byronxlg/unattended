Committed `7f2af43`. Not pushed; worktree clean.

Changed source notes to use calculation-specific wording and contributing-poll fieldwork dates; added four regression cases without editing existing tests.

Exact sentences: polls, “Polls parsed by this site.”; averages, “Available poll shares averaged with equal weight by this site.”; seats available, “Seats calculated by this site.”; seats withheld, “Seats withheld; see the headline.”

Thresholds: “Threshold shares averaged with equal weight by this site.” Validation retains “Calculation verified against captured final results.”

```text
pytest -q product/nz_election/tests
298 passed in 141.29s (0:02:21)

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (315 text files)
```

Both screenshot runs were blocked at Chromium launch by sandbox `Permission denied (1100)`. Screenshots and axe remain unverified. Host commands:

```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --og-only --out /tmp/ds-og
```