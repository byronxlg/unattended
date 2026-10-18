Committed brief first (`fcf3612`), then restyle (`28c8771`). **L-a remains incomplete:** this checkout has no coalition statements config, so allocator totals remain labelled grey. No memberships were invented.

Changed `web/styles.css`, `web/templates/home.html`, `web/fonts/*`; pipeline `{build,home,home_checks,market_panel,verify}.py`; five test files below. No push or `last.md` commit.

Pins moved, paths relative to `product/nz_election/`:

- `web/styles.css:1`: system sans → Libre Franklin 400/700; mono → JetBrains Mono 400.
- `web/styles.css:4`: ink `#000000→#222222`, grey `#5A5A5A→#6B6B6B`, rule `#8A8A8A→#949494`, surface `#F0F2F4→#FFFFFF`; added bloc/notice tokens. `tests/test_design.py:39` adds exact values and contrast pairings.
- `tests/test_design.py:83`: headline-only assertion → exact allocator party totals.
- `tests/test_design.py:115`, `pipeline/home_checks.py:40`: CSS `12,000→16,000`; measured **14,557 bytes**.
- `tests/test_design.py:117`: reserved 45 KB/no fonts → three required fonts counted in unchanged 100 KB limit; `tests/test_home.py:218` now expects the actual transfer-budget error.
- `tests/test_home.py:47`, `pipeline/home_checks.py:17`: election-date headline → “Who is favoured to form the next government?”
- `tests/test_build.py:62`, `tests/test_design_review.py:34`, `pipeline/verify.py:42`, home exclusion checks: “Poll history” → “How have the polls moved?”
- `tests/test_increment_two_regressions.py:90`: “Threshold watch” → “Which parties are near the 5 percent threshold?”
- `tests/test_home.py:171`: current-route markers follow five primary tabs instead of eight.

Fonts: `libre-franklin-400.woff2` **16,168 B**; `libre-franklin-700.woff2` **16,284 B**; `jetbrains-mono-400.woff2` **9,668 B**. SIL OFL 1.1 texts committed beside them; macron cmaps checked. First-view transfers: **home 55,494 B; polls 74,345 B**.

Verification:

```text
uv run product/nz_election/pipeline/verify.py all
PASS all
uv run product/nz_election/pipeline/build.py --data artifacts/la-data --out site/nz-election --now 2026-10-17T01:00:00Z
PASS build: 79 routes
uv run --with pytest pytest -q product/nz_election
568 passed in 234.40s (0:03:54)
bin/lint
lint ok (455 text files)
```

Host commands:

```sh
uv run product/nz_election/tests/screenshots.py --site site
uv run product/nz_election/tests/screenshots.py --site site --og-only
uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site site
```

Expected: `PASS screenshots: 79 routes, 296 images` (158+9+33+13+4+79); OG-only: `0 routes, 79 images`; `PASS coalition browser`. Full harness attempted, but Chromium hit macOS Mach-port `Permission denied (1100)`. Screenshots, axe and visual review remain unverified; checks were not relaxed.