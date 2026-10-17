Committed `bed5452`. Not pushed; worktree clean.

Local-poll captions and region names now identify pollster, measure, and fieldwork, with a suffix for duplicate descriptions. Source pairing is unchanged. Added one regression test; existing tests and axe checks are untouched.

Audited other table callers and confirmed unique region names across all 77 built routes.

Verification tails:

```text
pytest -q product/nz_election/tests
288 passed in 140.61s (0:02:20)

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (313 text files)
```

Could not run Chromium screenshots or axe in the sandbox. Browser verification remains unverified pending the host run.