Verdict: **accept** on static review. Runtime verification was blocked by the read-only sandbox.

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Checks:

1. `social.py:497` clears only the spent-day cap error. At `:574-581`, CLI emits `validated=true`, no reservation, and exits 0. The workflow publishes that status during reserve; `publish.py:225` accepts it. Artifact upload and downstream collection are skipped.
2. `social.py:515-516` retains `SOCIAL_CREDIT_CAP` for mid-collection exhaustion. Both collection and subsequent publication remain fatal.
3. `social.py:489-498` preserves last success and marks stale/unavailable. `social_page.py:74` gates charts by sample date, independent of error code. Null removes the redundant “Data to” line at `:48`, but sample dates remain visible. `verify.py` does not interpret null as fresh.
4. Against `6afc912`, existing test changes only update spent-day return/message expectations. Retention, accounting and single-use assertions remain; new tests cover both publication outcomes.
5. `runbook.md:213-215` matches the implementation.

Attempted:
```text
uv run --offline --with pytest pytest -q -p no:cacheprovider product/nz_election/tests/test_social.py product/nz_election/tests/test_social_publication.py
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open .../sdists-v9/.git: Operation not permitted (os error 1)
```

No files changed.