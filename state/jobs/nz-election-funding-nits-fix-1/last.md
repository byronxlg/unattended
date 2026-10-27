Committed `0125c17`; not pushed.

Updated `funding_page.py` and funding CSS: inline biggest-donors link, tighter intro/ranking gaps and pace-section spacing. Font sizes, mobile order and tests unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "funding or home or design"
10 failed, 151 passed, 2920 deselected in 144.72s

bin/lint
lint ok (1175 text files)
```

Chromium-denied checks:
- Phone type/targets: map, trend, header
- Home handover: absent, zero, complete, recovery
- Retirement: cached-after-stop, waiting-after-stop
- Night design browser

Screenshots and pace-answer y measurement were blocked by the same launch denial. Host visual verification remains open; details in uncommitted `last.md`.