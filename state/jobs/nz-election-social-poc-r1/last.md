Committed **`8faba3e`**, without amending or pushing. Working tree clean.

Route checks now verify the exact configured route set and uniqueness. The family test retains the hourly/daily race, then publishes social and checks the full union. Geography’s 77 correspondence records remain unchanged. Fixed my test’s output path and added `verify.py social`.

Results and decisions are recorded in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-social-poc/last.md).

```text
uv run --with pytest pytest -q product/nz_election/tests
331 passed in 165.89s (0:02:45)

uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data
PASS refresh: polls bundle

uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16
PASS social

uv run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election
PASS build: 78 routes

uv run product/nz_election/pipeline/verify.py all --data /tmp/sp-data --site /tmp/sp-site
PASS social
PASS all

uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots
CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed

bin/lint
lint ok (347 text files)

rg -n "X_UPSTREAM_KEY|TYPESAFE_API_KEY" --glob '!**/runbook.md' --glob '!.github/**' --glob '!**/social.py' product .github
No matches (exit 1).
```

**Remaining:** Chromium failed with sandbox permission denial. Run the screenshot command above on the host; screenshots and visual inspection remain unverified. No live X or Jev requests were made.