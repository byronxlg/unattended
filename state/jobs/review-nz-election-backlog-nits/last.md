**Verdict: request changes.**

- **Important - `product/nz_election/pipeline/funding_page.py:25`, `product/nz_election/tests/test_funding_totals.py:32`:** The actual home summary uses `feed()` → `headline()`, which still computes totals, rounding and counts independently of `funding_totals()`. The new test calls `funding_bars()` and its wrapper `ranking()`, so it compares the same renderer twice without exercising the home summary. Route the headline through the shared calculation and test the actual home summary against the funding ranking.

Verified read-only:

```text
PASS ranking: snapshot output unchanged (9 parties)
PASS snapshot: label and hidden-table counts unchanged
PASS both renderers: widths use exact cents
PASS landmarks: structural links, missing and duplicated banner/footer
```

New assertions do not pin markup, classes or bytes. Home output remains unchanged because its calculation path is untouched.

Local pytest rerun was blocked by uv cache permissions. Supervisor evidence: 86 passed, including Chromium. Screenshots were not independently reviewed. No files changed.