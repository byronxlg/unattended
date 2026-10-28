Committed `498932c`; not pushed.

- History windows now use shared hourly, daily and social sunsets. Unrecognised guards remain strict.
- Added 12 regression cases and updated the runbook. Existing tests unchanged.
- `last.md` records commit, verification and moved assertions: none.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden.py
262 passed in 0.60s

bin/lint
lint ok (1393 text files)
```

Combined suite: 274 passed. All 12 new cases failed before the fix on `origin/main`.

Open questions: none.