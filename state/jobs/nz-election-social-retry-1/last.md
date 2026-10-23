Committed `27dee94`; not pushed. Updated `social.py`, `social_page.py`, tests, and `evals/social-retry-budget/` for partial publication, coverage labels, strict provenance, and safe retry diagnostics.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests
1 failed, 2015 passed, 2 errors in 585.77s (0:09:45)

uv run product/nz_election/pipeline/verify.py social
PASS social

bin/lint
lint ok (820 text files)
```

All 204 focused social tests pass. Full-suite verification remains blocked: Chromium’s `bootstrap_check_in` returns `Permission denied (1100)`, affecting the party-picker test and two night-browser tests.

Eval on `28279a5`:
```text
FAIL retry budget: result=SOCIAL_CREDIT_CAP; 0 of 24 hours sampled; requests=24; reserved=7560; spent=3765
```

Eval on HEAD:
```text
PASS retry budget: result=ok; 23 of 24 hours sampled; requests=24; reserved=7560; spent=7560
```

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-social-retry/last.md) documents moved tests and conservative partial-run accounting. It remains uncommitted.