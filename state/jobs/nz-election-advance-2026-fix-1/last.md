Committed `44b052f`; not pushed. Isolated the authorized absence assertion and added verification of the committed capture. `last.md` remains uncommitted.

```text
uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home"
6 failed, 472 passed, 2622 deselected in 153.61s

bin/lint
lint ok (1283 text files)
```

Only Chromium sandbox-launch denials remain, all in `test_home_handover.py`:

- `test_browser_handover[absent]`
- `test_browser_handover[zero]`
- `test_browser_handover[complete]`
- `test_browser_handover[recovery]`
- `test_retirement_browser[cached-after-stop]`
- `test_retirement_browser[waiting-after-stop]`

Each reports `MachPortRendezvousServer: Permission denied (1100)`. No other failures.