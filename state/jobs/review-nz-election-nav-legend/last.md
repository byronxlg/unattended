Verdict: **request changes**. No confirmed production bug; required interaction coverage remains incomplete.

- **Important** - `product/nz_election/tests/header_nav_browser.py:28-39`: Each viewport starts a fresh page. This never exercises 390→844→390 rotation, retained scroll position, or opacity cleanup across the desktop breakpoint. Add same-page resize checks with a trailing current route and a focused link, asserting whole, painted targets and stable header geometry.
- **Important** - `product/nz_election/tests/header_nav_browser.py:39`: Keyboard verification checks bounds and outline style, but not opacity or visibility. Since this implementation hides links using opacity, an invisible focused link could pass. Add painted-visibility assertions after each Tab and Shift+Tab, plus manual-scroll checks.

The exact-source inline exception matches the script policy. No-JS links retain native scrolling and keyboard access; opacity preserves accessibility exposure. Legend grouping looks correct, and the inspected host captures show whole labels and visible current tabs on primary routes.

Verification: `node --check product/nz_election/web/header-nav.js` passed; read-only policy probe printed `PASS exact inline handler allowed`. Relied on the supplied **163 passed** host result; did not rerun Chromium or independently verify rotation. No files changed.