Verdict: **request changes**.

- **Critical:** None.
- **Important:** `product/nz_election/pipeline/home.py:221`, `product/nz_election/pipeline/snapshot_views.py:101`: Required visual verification is missing. These changes introduce `display:contents` seat wrappers and SVG `<use>` tiles, but no 390×844 or 1280×800 screenshots are available; `artifacts/browser.txt` records Chromium failing to launch. The question test, seat colours/layout, and map focus appearance remain unverified. Provide populated screenshots and a passing browser check before acceptance.
- **Nit:** None.

Read-only checks found no functional regression:

- No existing byte, transfer, font, or screenshot budgets changed.
- In-memory base/head rendering preserved all home text, ARIA attributes, existing IDs, and link targets, with question order unchanged.
- All 71 other-route map renderings were byte-identical.
- New regression tests exercise populated seats and electorate results.
- Eval retains `verify.py all`, pinned incident data, and `pipefail`.

Independent measurement output:
```text
base: FAIL html_bytes 68868
head: PASS html_bytes 59724
home text identical: True
home aria/ids/link targets identical: True
71 other-route maps byte-identical: True
```

Full eval/test reruns were restricted by the read-only sandbox. Existing eval output says `PASS all`; existing suite output reports `1 failed, 1960 passed, 2 errors`.