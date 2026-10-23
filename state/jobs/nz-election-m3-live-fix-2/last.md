Committed `8da4d3a`; not pushed.

- Recovery now reconciles the data SHA against the served Pages manifest.
- Successful unchanged acquisitions update freshness through full Pages deployment. Budget: roughly `60 + 12P` runner-minutes/hour.
- Both regressions fail on `727561e` and pass now.
- Required suite: **49 passed, 2 Chromium sandbox setup errors**.
- Night verifier and lint pass.

Evidence is in uncommitted `last.md`. Host browser rerun remains required.