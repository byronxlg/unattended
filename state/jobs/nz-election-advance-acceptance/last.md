Committed `b534af3`; not pushed.

Added opt-in `--require advance` acceptance, stable failure codes, both-page count/date checks, and distinct nonzero `ADVANCE_GAP`. Updated verify, harden help, runbook, and added tests. Existing tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py product/nz_election/tests/test_harden*.py
488 passed in 321.72s (0:05:21)

bin/lint
lint ok (1307 text files)
```

Against origin/main’s verifier: four regression tests failed as expected, proving omitted/stale captures and incorrect page counts previously passed.

Commands, evidence, and supervisor instructions are in uncommitted `last.md`. Open questions: none.