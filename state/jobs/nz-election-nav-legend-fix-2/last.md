Committed `fddc5df`; not pushed. Legend unchanged.

Replaced experimental CSS with a validated inline handler that measures links, reveals the current route, and hides partial edge labels. Added JS-enabled geometry tests; protected checks remain unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"
11 failed, 152 passed, 2927 deselected in 146.47s

bin/lint
lint ok (1287 text files)
```

All 11 failures were Chromium sandbox-launch denials:
- Phone checks: map, trend, header
- New header navigation check
- Handover: absent, zero, complete, recovery
- Retirement: cached-after-stop, waiting-after-stop
- Night design browser

Script-policy checks: 2 passed.

Screenshots and browser comparison against `17d5f7f` remain blocked. Details in uncommitted `last.md`.