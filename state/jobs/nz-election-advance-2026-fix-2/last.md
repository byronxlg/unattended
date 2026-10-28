Committed `10ea076`; not pushed.

Both pages now show “Transcribed from the EC page, not downloaded.” from provenance data. Missing provenance adds no disclosure. Branch-owned tests cover both full pages; protected tests unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home"
6 failed, 472 passed, 2622 deselected in 150.74s

bin/lint
lint ok (1283 text files)
```

Only Chromium sandbox-launch denials remain in `test_home_handover.py`:

- `test_browser_handover[absent]`
- `test_browser_handover[zero]`
- `test_browser_handover[complete]`
- `test_browser_handover[recovery]`
- `test_retirement_browser[cached-after-stop]`
- `test_retirement_browser[waiting-after-stop]`

The same denial prevented screenshots. Fixture-build text verified on both pages. `last.md` remains uncommitted.