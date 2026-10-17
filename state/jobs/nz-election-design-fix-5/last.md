Committed `0108d71`. Not pushed; worktree clean.

1. Empty windows render unavailable; new regression and baseline comparison render, and empty-window verification passes.
2. Restored full strip/table equality and numerical position, width, marker, and connector checks.
3. Python/JS strip markup matches exactly, including accessibility, table columns, disclosures, and precision; three Node parity cases cover overhang.
4. Source labels derive per source; original links and licences are visible outside disclosures.
5. Compact provenance prose, wrapping 44 px action rows, and unpadded OG links implemented. Visual review remains pending.
6. Methods link remains visible in both unavailable forms.
7. One pipeline presentation record supplies page and OG availability, headline, selected polls, and provenance.
8. Per-route OG publication and `og:image`: deferred as requested.
9. Focus nit: main is blurred after testing; skip-link and main focus get separate captures.
10. Unavailable OG whitespace: deferred as requested.

Verification tails:

```text
pytest -q product/nz_election/tests
294 passed in 141.04s (0:02:21)

Final targeted design/review tests
24 passed in 22.24s

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (314 text files)
```

CSS: 11,000 bytes. Built home transfer: 17,858 bytes before reserved font.

Both screenshot commands failed at Chromium launch with sandbox `Permission denied (1100)`. I could not inspect the requested images or verify browser axe results. Host commands:

```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --og-only --out /tmp/ds-og
```