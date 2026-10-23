**Verdict: request changes.**

**Critical:** None.

**Important**

- `product/nz_election/pipeline/social.py:508`: The spent-day status retains `error_code='SOCIAL_CREDIT_CAP'`. Although the CLI exits 0 and emits `validated=true` without a reservation ID, `.github/workflows/nz-election-social-daily.yml:62-65` then invokes the publisher. `product/nz_election/pipeline/publish.py:224-227` publishes that status and exits nonzero for any error code. The reserve job therefore remains red; collection and subsequent publication are skipped. In-memory reproduction:
  ```text
  {"outcome": "published"}
  publisher exit: FAIL refresh: handled failure status published ; publish calls: 1
  ```
  Carry the benign spent-day distinction through publication while preserving fatal mid-run caps. Add workflow-level coverage. The runbook’s clean-exit claim (`product/nz_election/runbook.md:213`) is currently true only for the collector.

**Nit:** None.

Other checks:

- Spent-day branch makes no upstream call, appends no ledger row, preserves daily/credits files through copying, and writes status. New tests assert byte identity for all social files.
- Existing reservations bypass `budget_spent`; allocation consumption and mid-run cap failure remain unchanged.
- Arithmetic probes passed: remaining 314 → spent; 315 and 316 → not spent. NZ midnight correctly excludes yesterday’s reservations. Equality is unreachable with current valid ledger multiples, but the comparison is correct.
- Both status variants read correctly; “no previous data” was removed.
- Existing entry freeze guards and publication guard remain intact. The new early return bypasses the collector’s final clock recheck, but publication independently checks the freeze.
- Main’s tests were not weakened beyond the explicitly authorized contract changes. `verify.py` retains daily-byte retention and adds both ledger-file comparisons.

Verification limits: pytest, lint, and verify all stopped with `Failed to initialize cache ... Operation not permitted`. `gh pr view 56` failed to connect to GitHub, so the PR body remains unchecked. No files changed.