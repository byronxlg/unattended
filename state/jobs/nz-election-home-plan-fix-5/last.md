Committed `bc8ffb2`, not pushed.

Restored six-digit tokens without changing values. CSS remains within budget at 18,999 bytes; Fix-1 through Fix-4 behaviour is preserved.

- `test_design.py`: **19 passed**
- Full suite: **1925 passed, 1 failed, 2 errors**
- Lint: `lint ok (644 text files)`

All three unsuccessful cases are Chromium startup failures (`Permission denied (1100)`): party-picker sizing, XML/browser parity, and replay network checks.

Rebuilt before, after and night. `last.md` and artifacts remain uncommitted.