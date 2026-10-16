Committed **`91ebf33`** on `change/nz-election-design`. Not pushed; worktree clean. Rebased onto merged PR #16; no changes to `verify.py`.

Restyled all 77 routes, added identity assets, state fixtures and design checks. [Full report](/Users/byron/repos/unattended/.worktrees/nz-election-design/product/nz_election/DESIGN_REPORT.md) lists every route change and modified assertion with draft-2 line references.

- CSS: **10,609 bytes**
- Home transfer: **17,478 bytes**; coherent fixture including startup JSON: **30,685 bytes**
- Estimated source-note bottom at both 360 and 390: **456.8 px**, or **670.8 px** with seats. Browser measurements pending.

Verification tails:

```text
pytest:                287 passed in 144.42s
refresh/build/verify:  PASS all
screenshots:           NOT RUN: Chromium unavailable in sandbox
bin/lint:              lint ok (313 text files)
```

Tests: 269 existing + 18 additions, none removed. Axe needed no lint exemption.

Host commands still required:

```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-og --og-only
```

Screenshots, axe results and visual review remain unverified.