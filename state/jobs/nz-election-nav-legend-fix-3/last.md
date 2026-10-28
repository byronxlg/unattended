Committed `8bc1aae`; not pushed. Legend unchanged.

Added resize, keyboard-paint, and manual-scroll checks. Fixed visible-link opacity (`1`) and current-route priority during resize. Updated `DESIGN.md`.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"
11 failed, 152 passed, 2927 deselected in 146.62s

bin/lint
lint ok (1287 text files)
```

All failures were Chromium sandbox-launch denials:

- Phone checks: map, trend, header
- Header navigation
- Handover: absent, zero, complete, recovery
- Retirement: cached-after-stop, waiting-after-stop
- Night design browser

Uncommitted `last.md` names each new check and its baseline status. Simulations reproduce the opacity and focused-resize defects in `fddc5df`; browser comparisons and screenshots remain blocked.