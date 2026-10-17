Committed **`1271c0e`**, not pushed.

- Both social source notes now use `div.source-note` with link-free prose and links in `p.source-actions`.
- CSS and tests unchanged. Markup matches the existing 44 px rule.
- `last.md` removed from tracking and retained on disk with verification details.

Verification:
- Tests: **331 passed in 165.34s**.
- Fixture pipeline: **PASS social**, **78 routes**, **PASS all**.
- Lint: **lint ok (346 text files)**.
- Secret-name scan: no matches outside allowed files.
- Screenshots: Chromium launch blocked by sandbox permissions.

Host must run and inspect:
```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/sp-site --out /tmp/sp-shots
```

No live X or Jev requests.