# Home defects, issue 34

Base: `4dbb18edbe6eefb5c92dd044e82ade47396d24b7` (after PR 37).
Read the issue's final review and design principles. Only defects 5-9 and 11 addressed.

## Causes and changes

- 5: `threshold_watch` deliberately includes the 2-7% neighbourhood, including parties above 5%. The home renderer ignored the share when choosing qualification text. Keep the selection and values; compare the exact value/scale against 5 before checking electorate assumptions. Heading now `Qualification`. Tests cover 4.99%, exactly 5%, and Opportunity at 6.2%.
- 6: Latest polls hardcoded three party columns. Select the union of parties at least 5% in the displayed polls and those with electorate wins in the existing seat assumptions. Use the source registry order for both latest polls and trend, including Opportunity. Missing observations remain `Not reported`.
- 7: Home printed normalized pollster IDs and inherited numeric-cell monospace. Reverse the existing source-name mapping, escape names (including unknown fallback names), and use the text face for row labels. No invented Talbot Mills/Anacta alias.
- 8: Top-aligned cells placed unpadded margin text above links with 10px vertical padding. Baseline-align the cells, retain 44px links and focus outlines, and use text-face row names with quiet links and hover/focus underlines.
- 9: The short market label stripped the proposition. Home now shows a question before each price, preserving the subject and seat interval while removing repeated NZ election context. Caption is `Leading market choices: price for Yes`. Selection, prices, IDs and full terms on Methods remain intact.
- 11: Added explicit 100% width/max-width bounds to the hero figure and bar, with zero minimum width, inside the padded main column. The reported overflow's root cause could not be reproduced in this sandbox. This is a containment guard, not a verified browser fix; supervisor confirmation remains required.

Files: `pipeline/home.py`, `pipeline/market_panel.py`, `web/styles.css`, `tests/test_markets.py`, new `tests/test_home_defects.py`, this report (product-relative paths).
No new source. Existing figure IDs, source-note links and Methods provenance retained.
One permitted text assertion changed: `test_markets.py::test_home_market_summary_and_all_page_filtering` pinned the defective short seat labels (`National Party: 35-39 seats`, `Labour Party: 35-39 seats`). It now requires the complete reader-facing questions for all four selected contracts. No harness assertion changed.

## Verification

- `uv run --with pytest pytest -q product/nz_election/tests/test_home_defects.py product/nz_election/tests/test_build.py`: `16 passed in 7.42s`.
- Six defect checks against an archived base, with only the new test file copied in: `6 failed, 3 deselected in 3.16s`. Use `uv run --with pytest python -m pytest --rootdir=. --confcutdir=. --import-mode=importlib -q product/nz_election/tests/test_home_defects.py -k 'test_5 or test_6 or test_7 or test_8 or test_9 or test_11'` from the archived root. Import isolation matters for a nested archive.
- Checks 5, 6, 7 and 9 inspect built, populated HTML; 8 and 11 inspect shipped CSS contracts. CSS checks do not prove browser geometry.
- `uv run product/nz_election/pipeline/verify.py all`:
  `PASS polls`, `PASS thresholds`, `PASS provenance`, `PASS pipeline`, `PASS coalitions`, `PASS geography: 64 general, 7 Māori`, `PASS candidates: 71 electorates`, `PASS electorates: 71 pages`, `PASS social`, `PASS home`, `PASS home-routes`, `PASS markets`, `PASS all`.
- `uv run --with pytest pytest -q product/nz_election/tests/test_home_defects.py`: `9 passed in 5.60s`.
- `bin/lint`: `lint ok (493 text files)`.
- `uv run --with pytest pytest -q product/nz_election`: `660 passed in 298.47s (0:04:58)`.

## Geometry and budget inventory

Identical populated offline inputs before/after: refresh ending 2026-07-18, daily fixtures, build time `2026-10-17T01:00:00Z`. These are historical/synthetic observations, not a live-data claim.

| Check affected or preserved | Before | After | Limit |
|---|---:|---:|---|
| measure_home details | 0 | 0 | 0 |
| measure_home h2 | 7 | 7 | <=7 |
| measure_home links | 37 | 37 | <60 |
| measure_home source occurrences | 7 | 7 | <12 |
| measure_home HTML bytes | 10699 | 11217 | <35000 |
| CSS bytes | 14965 | 15338 | <16000 |
| Combined HTML/CSS bytes | 25664 | 26555 | <200000 |
| HOME_MARKET_HEIGHT at 390 | unmeasured | unmeasured | <=844px |
| SOURCE_NOTE_BELOW_FOLD, 360/390 | unmeasured | unmeasured | bottom <=780px |
| PAGE_OVERFLOW, 360/390/1280 | unmeasured | unmeasured | scrollWidth <= viewport |
| SMALL_TARGET | unmeasured | unmeasured | height >=44px |
| HOME_ROW_KEYBOARD_FOCUS | unmeasured | unmeasured | 1 focused row link |
| AXE landmark-unique | unmeasured | unmeasured | 0 violations |
| Seat bar relative to text column | unmeasured | unmeasured | both edges inside column |

No geometry assertion was edited. Numeric browser results cannot be supplied honestly:
`uv run product/nz_election/tests/screenshots.py --site site --out site/defect-review/screenshots` fails before rendering with `CHROMIUM_REQUIRED`, `bootstrap_check_in ... Permission denied (1100)` from Chromium's MachPortRendezvousServer. Installed Chromium was used; no browser download attempted. Screenshots were not produced or inspected. The supervisor must run the existing populated harness and inspect 360/390/1280 before treating the geometry requirements and defect 11 as complete.

Local ignored artifacts: `site/defect-review/data`, `site/defect-review/before`, `site/nz-election` (after), and `site/defect-review/base-src` (archived base with new regression tests).
