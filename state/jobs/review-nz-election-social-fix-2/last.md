Verdict: **accept with nits**

1. **Nit** - `product/nz_election/pipeline/social_page.py:83`: The caption overstates query coverage. National/Labour/Greens are unquoted contextual terms, and not every party has a short-form phrase. Replace with: “The search combines selected hashtags, leader names and party terms; each day’s provenance records the exact query.”

Requested verification was blocked by the read-only sandbox:

- `evals/social-query-length/check.sh`: `cannot create temp file for here document: Operation not permitted`
- `uv run --with pytest pytest -q product/nz_election/tests/test_social_diagnostics.py product/nz_election/tests/test_social.py`: `Failed to initialize cache at /Users/byron/.cache/uv`
- `bin/lint`: same uv cache failure.

Additional in-memory probe output:
```text
actual query length 495
512 accepted calls 24 reserved 7560 sent lengths [512]
513 SOCIAL_QUERY_TOO_LONG calls 0 reserved 0 sent lengths []
```

Full test verification remains outstanding.