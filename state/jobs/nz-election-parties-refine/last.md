Committed `10d31ce`; not pushed.

- `snapshots.py`: source-specific licences enforced; all 14 committed records remain valid.
- `parties_page.py`: credit separators join only non-empty parts.
- `test_parties_refine.py`: 13 regression cases. Existing tests unchanged.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests
1 failed, 1933 passed, 2 errors in 557.70s
```

All three unsuccessful cases were blocked by Chromium launch permission errors: party picker and two night-page browser tests.

```text
bin/lint
lint ok (651 text files)

PYTHONPATH=. uv run python -m product.nz_election.pipeline.verify all
PASS all
```

On base `729f9e7`, before production edits:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_parties_refine.py --tb=short
9 failed, 4 passed in 3.93s
```

After fixes: `13 passed`. Missing-source tests already passed on base; that behavior was already correct.

Host follow-up: rerun browser tests and inspect populated parties/ at 390x844 and 1280x800 for credit punctuation, links and wrapping. Details in uncommitted `last.md`; logs in uncommitted `artifacts/`.