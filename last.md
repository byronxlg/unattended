# Social proof of concept: follow-up 1

Route contracts now derive the exact expected paths from `config/routes.json`
and `config/electorates.json`, the build's inputs. Tests assert path equality
and registration uniqueness. The screenshot harness checks that every route
has exactly one capture at each of 390 and 1280 pixels. Its PASS count is derived.
`test_geography.py:29` remains 77: those are electorate boundary correspondence
records, not routes. The 71-electorate checks are unchanged.

Chose to publish all three owned families in the union test: keep the hourly/daily
race and lease retry assertion, then publish synthetic social data through
`publish(..., family='social')`. The unchanged full family and status union checks
now apply after all owners publish. Byte-for-byte preservation checks also cover
nested social files. The supplied all-families fixture similarly includes social;
its family-union assertion remains unchanged. No production ownership changes.

The social build test now writes to `site/nz-election`, as `output_path` requires.
`verify.py social` and `verify.py all` exercise synthetic collection, credit
accounting and cap retention, identifier rejection, attitude withholding, freeze
boundaries, and present/absent/stale page behavior. Supplied bundles continue
through `export.validate_bundle`, including the social schema and ledger checks.
The first CLI run exposed a relative-import error in the new check; fixed to use
the same absolute imports as the other verification checks and reran it.

No live X or Jev requests. No assertions unrelated to routes or family sets were
edited. All social transports are injected synthetic fixtures.

## Verification

Final command outputs follow, including the sandbox screenshot limitation.

Screenshots: `uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots`
failed at Chromium launch, after passing the route assertion:

```text
CHROMIUM_REQUIRED: BrowserType.launch: Target page, context or browser has been closed
bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer: Permission denied (1100)
```

No screenshots were produced or visually verified. On the host, outside the
sandbox, run the same command from this worktree. It will capture the social page
at 390x844 and 1280x800 along with the other registered routes.

Final fixture command (an earlier generated `/tmp/sp-data` was moved aside so
its persistent credit ledger would not correctly reject this verification rerun):

```sh
uv run product/nz_election/pipeline/refresh.py --fixtures --out /tmp/sp-data && uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/sp-data --day 2026-10-16 && uv run product/nz_election/pipeline/build.py --data /tmp/sp-data --out /tmp/sp-site/nz-election && uv run product/nz_election/pipeline/verify.py all --data /tmp/sp-data --site /tmp/sp-site
```

```text
Offline verification: immutable captures, not live data
PASS refresh: polls bundle
PASS social
PASS build: 78 routes
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS social
PASS all
```

`bin/lint`: `lint ok (347 text files)`.

```sh
rg -n "X_UPSTREAM_KEY|TYPESAFE_API_KEY" --glob '!**/runbook.md' --glob '!.github/**' --glob '!**/social.py' product .github
```

No matches, exit 1 as expected. An additional local HTML assertion confirmed
`Proof of concept` is present and `@` is absent from the generated social page.

`uv run --with pytest pytest -q product/nz_election/tests`:

```text
331 passed in 165.89s (0:02:45)
```

Remaining verification: host Chromium screenshots and visual inspection. Live
upstreams and Actions execution were intentionally not exercised. No other
existing-test blocker occurred. Changes are committed locally, without pushing.
