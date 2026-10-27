Committed `3304028`, not pushed.

Updated shared header CSS/template, footer route rendering, design docs and tests. Chose horizontal scrolling with a visible cue, preserving 16 px text and 44 px targets.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "design or home or nav or header"
10 failed, 156 passed, 2914 deselected in 144.08s

bin/lint
lint ok (1175 text files)
```

All 10 failures were sandbox-denied Chromium launches. Header measurements and screenshot review remain for the host run. Details and blocked test names are in uncommitted [last.md](last.md).