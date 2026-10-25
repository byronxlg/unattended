Committed `dcf467d`. Not pushed.

- `check_workflow_history.py`: unsupported shell syntax invalidates the entire step’s guard evidence.
- `test_harden.py`: regressions added; protected tests unchanged. One branch-owned ANSI-C expectation updated.
- All four required regressions failed on `d406b7f`.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py
203 passed in 0.32s

bin/lint
lint ok (996 text files)
```

Hourly’s real guard remains recognized. Night-live’s complex step now provides no guard evidence, the permitted false negative. Details and outputs are in uncommitted `last.md`.

Open questions: none.