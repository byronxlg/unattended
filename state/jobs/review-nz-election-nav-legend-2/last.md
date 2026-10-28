Verdict: **accept**. Review recommendation only, not approval.

No Important or Nit findings.

- `web/header-nav.js:10-12` paints whole links at opacity 1 and clipped links at 0.
- `web/header-nav.js:25-31` prioritizes the current route during resize; focus changes reveal the focused link.
- `tests/header_nav_browser.py:51-118` checks same-page resizing, real keyboard traversal, computed opacity and geometry, plus manual scrolling.

Verification: reviewed the product diff and four available screenshots. Relied on supervisor evidence: **163 passed**, with the prior implementation failing `HEADER_INTERMEDIATE_OPACITY`. Browser tests were not rerun in this read-only session; full dark-mode and before/after visual coverage remains unverified.