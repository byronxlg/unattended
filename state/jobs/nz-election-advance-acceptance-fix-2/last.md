Committed `20b6792`; not pushed.

Updated `advance_acceptance.py` to conservatively exclude all 21 classes found in hiding/clipping selectors. Added both-route regressions and a stylesheet drift guard. Main-base tests untouched.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py product/nz_election/tests/test_harden*.py
563 passed in 389.15s (0:06:29)

bin/lint
lint ok (1311 text files)
```

Against `65fbef1`: `42 failed, 2 passed`, demonstrating the regressions.

Uncommitted `last.md` records the class inventory, mechanism, commands and outputs. Open questions: none.