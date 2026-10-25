Verdict: **request changes**

- **Critical:** None.
- **Important:** `product/nz_election/pipeline/verify.py:431-441`: With both `--data` and `--site`, presence checking covers only `--data`. If that bundle contains night but the site’s manifest lists a missing `night/index.json`, site validation produces `CAMPAIGN_DATA`, not `MISSING_NIGHT_FAMILY`. Check both supplied locations before validation.
- **Nit:** None.

Read-only Python probes with mocked filesystem/validators confirmed:
- 32 missing-family paths returned `MISSING_NIGHT_FAMILY`, exit 1.
- Optional dispatch printed both SKIP lines, no night/waterfall PASS, exit 0.
- Combined flags with bundle present/site absent reproduced `FAIL all: CAMPAIGN_DATA`.

No existing tests from `7ecf80a` changed; only two test files added. Pytest was not run. No files changed.