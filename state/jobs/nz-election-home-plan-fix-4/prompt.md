# nz-election-home-plan fix-4 (PR #64, second fresh review on 801c204)

Second fresh review: request changes, one Important.
- `product/nz_election/web/styles.css:6`: this branch removed `.home-picker .home-directory{display:block}`.
  Without it the desktop four-column `.home-directory` grid applies to the picker's single link, and at
  1280x800 "Browse all electorates and candidates" wraps into a narrow stack of broken words
  (`screenshots-before/home-1280x800.png`). Restore a picker-specific rule so the link reads on one or two
  lines at 1280, and keep the 26 x 26 picker targets at 360 and 390 and the 44 px link floor.

Also add a check that would have caught it (in this branch's own home checks, e.g. the link's rendered
width at 1280 is at least the width of its longest word, or the picker directory is not a multi-column
grid); show it failing on 801c204 and passing on HEAD in last.md. Tests on main at de9a7c2 may not be
weakened; this branch's own tests may move. Thresholds and screenshots.py unchanged.

Definition of done:
- Same pytest command as fix-3 passes (browser tests may not start in your sandbox; say so); `bin/lint` ok.
- Rebuild `artifacts/nz-election/before`, `after`, `night` with your code; if Chromium starts, run
  `uv run artifacts/nz-election/fix1/check-review.py` (expect exit 0); if not, say so and the supervisor
  reruns it on the host.
- Commit on change/nz-election-home-plan; do not commit last.md or artifacts/.
