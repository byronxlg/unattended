Verdict: **request changes**.

**Critical:** None found.

**Important:**
- `product/nz_election/tests/night_browser.py:134`: Rendered target sizes and required screenshots remain unverified. Existing logs show Chromium launch failures; no screenshots are available. Run the populated browser harness on a capable host and inspect the 390×844 and 1280×800 images before closing the UI findings.

**Nit:** None.

The four fixes have regression coverage. Executing the ten new test cases directly in memory, including the Node parser:
```text
ec9d3fb 10 passed, 0 failed
467512b 0 passed, 10 failed
```
Map bounds, named ties with margin zero, table selection markup/CSS, and runbook assertions pass. Selection now uses table links; hexagons are non-interactive. No existing main check was weakened.

Limitations: `uv` was blocked by read-only cache permissions. GitHub comments were unreachable, so review used your supplied first-review findings. No files changed.