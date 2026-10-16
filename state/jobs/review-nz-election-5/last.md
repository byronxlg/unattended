- **Important** - [pipeline/export.py:287](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/pipeline/export.py:287): Existing bundles must equal the current checkout’s registry and configuration hashes. A reviewed correction therefore invalidates last-good geography before hourly refresh, daily refresh or publication can advance. **Reproduction:** changing one registry note in memory makes the existing valid bundle raise `REGISTRY_MISMATCH`. **Fix:** distinguish snapshot-integrity validation from current-input validation, allowing independent family replacement and retention.

- **Important** - [web/electorates.mjs:5](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/web/electorates.mjs:5): Lowercasing does not implement Python’s case folding. **Reproduction:** `Eaſt Coaſt` becomes `east coast` in Python but remains `eaſt coaſt` in JS, missing East Coast. `Tamaki` and doubled spaces work. **Fix:** use equivalent normalization in both implementations and test parity.

- **Important** - [tests/test_geojson.py:57](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/tests/test_geojson.py:57): Reference companions bypass required capture-integrity validation. Neither companion has a manifest entry; the test reads their bytes directly and only checks that the claimed input hash differs from the simplified capture. **Reproduction:** changing companion bytes never triggers `CAPTURE_HASH_MISMATCH`. **Fix:** manifest both companions and load them through `captures()` before comparison.

- **Important** - [tests/test_geography.py:58](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/tests/test_geography.py:58): The page-budget gate measures one generator result, not all inline and linked SVG required by the rendered page. **Reproduction:** an in-memory render containing two maps totals **568,632 bytes**, while `test_svg_page_budget` still passes. **Fix:** measure SVG resources from the rendered page, retaining the separate outline gate.

Read-only probes passed registry/correspondence identity and totals, stable slugs after renaming, unresolved fallback, malformed-coordinate rejection, SVG links/holes and colour evidence. Current SVG sizes: **284,316 / 15,339 bytes**. Independent-reference area differences: **0.03399% general / 0.03484% Māori**, in projected square metres. Numeric-property string conversion is documented; inspected consumers do not require those properties numeric.

The existing-test diff also excludes SVG anchors from the 44px check and search controls from static-text equality; both preserve the intended fallback checks. The claimed **11-file hourly parity** lacks a committed cross-reference comparison: current regression tests compare six poll-family files within this branch. I did not independently reproduce the 11-file comparison.

Screenshot observations:

| Image | Observed |
|---|---|
| `electorates-390x844` | Clear silhouette, quiet readable selectors; directory below viewport; no visible horizontal overflow. |
| `electorates-1280x800` | Map dominates beside readable directory links; southern map extends below viewport. |
| `map-general-390x844` | General boundaries visible; blue radio focus with white separation; search near viewport bottom. |
| `map-general-1280x800` | General layer beside directory; blue radio focus visible. |
| `map-maori-390x844` | Māori layer visibly distinct; readable selector, but no focus ring captured. |
| `map-maori-1280x800` | Māori layer visible; directory still begins with general seats; no focus ring captured. |

CSS supplies 44px directory links and contrasting boundaries; selector switching requires no JS. Missing Māori focus in these mouse-driven captures does not establish a keyboard defect. Full suite not rerun: uv cache writes were denied; Chromium was not launched. No files changed.

Important findings: 4