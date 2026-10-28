Committed `789e2bd`. Not pushed; `last.md` remains uncommitted.

Changed `styles.css`, `home_graphics.py`, `screenshots.py`, and `DESIGN.md`:
- Phone nav uses two whole-label slots with the existing scroll cue.
- Legend keeps blocs together, followed by “Other parties.”
- Added bounding-box clipping checks at 360/390.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"
10 failed, 151 passed, 2927 deselected in 145.30s (0:02:25)

bin/lint
lint ok (1284 text files)
```

All failures were Chromium sandbox-launch denials:
- Phone type/targets: map, trend, header
- Handover: absent, zero, complete, recovery
- Retirement: cached-after-stop, waiting-after-stop
- Night design browser

Could not take screenshots at 360×844, 390×844, or 1280×800. Visual verification and confirming the regression check fails on base remain for the host. No open questions.