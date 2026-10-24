Verdict: accept.

Critical / Important / Nit: none.

- `product/nz_election/web/coalitions.mjs:166`: Both messages explain the cause and suggest corrective action, without banned absent wording. `[data-live]` is reader-visible, not screen-reader-only; the revised copy resolves the previous finding.
- `product/nz_election/tests/coalitions_browser.py:170`: Runs `check_absent_text` on escaped runtime `[data-live]` text. The replacement assertion requires the full actionable tie message; all empty-picture, unassigned-count, and recovery assertions remain. No assertion is weaker.
- `product/nz_election/tests/coalitions_browser.py:157`: Routes match the module-relative fetch at `web/coalitions.mjs:141`: `/unattended/nz-election/data/{averages,seats}.json`.

Reviewed `git diff 8a8d484...deecb15 -- product` against REVIEW.md. Host-reported verification: `PASS coalition browser`. Browser checks and screenshot assessment were not independently repeated in this read-only review. No files modified.