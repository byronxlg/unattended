Committed `d540336`; not pushed.

Changed `advance_preflight.py` and branch-owned tests. Diagnostics use fixed messages; `kind_inference` remains unchanged. Audited parser error paths; no parser changes needed.

Verification:

```text
Marker regression on 7192300: 2 failed
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py
122 passed in 16.80s
bin/lint
lint ok (1028 text files)
```

Protected tests unchanged. Results recorded in uncommitted `last.md`. Open questions: none.