**Verdict: request changes.**

- **Important: visible readability is not verified** at `product/nz_election/tests/funding_rows_browser.py:53-60`. Accessible names plus `is_visible()` can pass for transparent, clipped or offscreen text. Cell width checks do not establish viewport containment or detect vertical clipping. Check rendered text and its geometry, scrolling each return into view, while retaining the accessibility assertions.
- **Important: subprocess lifetime is unbounded** at `product/nz_election/tests/test_funding_rows.py:10-14`. Without a timeout, a stalled browser worker can hang pytest indefinitely. Bound execution and ensure timeout cleanup covers browser descendants. Server cleanup also starts too late: snapshot loading at `funding_rows_browser.py:31` can raise before entering `try`.
- **Nit: overflow diagnostics lack context** at `product/nz_election/tests/funding_rows_browser.py:44,60`. Page failures omit the party; cell failures omit party, return and field. Include those identifiers and measured dimensions.

Checks satisfied by inspection:

- Restoring effective `min-width:620px` would fail: phone rules currently set `min-width:0` and `overflow:visible`; document or region overflow assertions would detect the widened table.
- Both phone widths iterate every party and return from the same snapshot used by the build. Expected values derive from records.
- Locators use accessibility roles without asserting markup, classes or source bytes.

Verification limitations:

- Confirmed HEAD `cb8e937`; reviewed existing `git diff origin/main...HEAD`, containing only the two requested files.
- `git fetch origin` failed: `FETCH_HEAD: Operation not permitted`.
- `uv run --with pytest pytest -q product/nz_election/tests/test_funding_rows.py` failed before tests: `Failed to initialize cache at /Users/byron/.cache/uv ... Operation not permitted`.

No files changed. Fresh remote comparison and runtime verification remain unverified.