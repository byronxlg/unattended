Committed `17d5f7f`; not pushed. Legend unchanged.

Changed `styles.css`, `screenshots.py`, and `DESIGN.md`: natural-width tabs, whole-tab edge hiding, initial current-route scrolling, and stronger visibility checks.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"
10 failed, 151 passed, 2927 deselected in 143.75s

bin/lint
lint ok (1284 text files)
```

All failures were Chromium sandbox-launch denials:
- Phone targets: map, trend, header
- Handover: absent, zero, complete, recovery
- Retirement: cached-after-stop, waiting-after-stop
- Night design browser

Screenshots and regression comparisons against both earlier versions remain unverified. The CSS approach requires view-timeline and `scroll-initial-target` support; older browsers retain native scrolling without these guarantees.

Details in uncommitted `last.md`.