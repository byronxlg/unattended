Committed `df01417`, not pushed.

Added CSS scroll padding to reveal focused links fully; updated design docs. Tests unchanged.

Verification:
```text
pytest: 10 failed, 156 passed, 2914 deselected
bin/lint: lint ok (1175 text files)
```

All failures were sandbox-denied Chromium launches. Uncommitted `last.md` records the change and required host verification.