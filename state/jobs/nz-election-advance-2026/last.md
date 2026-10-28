Committed `4ae0d41`, not pushed. Added EC capture/manifest, preflight declaration support, sourced vote/home lines, and 11 tests. Existing tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home"
7 failed, 470 passed, 2622 deselected in 149.52s
```

One blocking failure: `test_require_year_missing_and_registered_invalid` assumes no committed 2026 capture. Changing it falls outside the permitted test edits.

Chromium sandbox launch denials:
- `test_browser_handover[absent, zero, complete, recovery]`
- `test_retirement_browser[cached-after-stop, waiting-after-stop]`

These also prevented screenshots.

```text
uv run python product/nz_election/tools/advance_preflight.py product/nz_election/fixtures/ec-2026/advance-voting-2026-10-28.csv --url https://vote.nz/2026-general-election/about/overview/voting-statistics --kind daily
PASS advance preflight

bin/lint
lint ok (1283 text files)
```

Both home and vote fixture builds render:

> 175,748 advance votes reported through 27 October. Informal count, subject to revision; excludes overseas votes. Electoral Commission. Retrieved 28 Oct, 20:08 NZDT.

Report: [last.md](last.md). The requested green-test gate remains unmet.