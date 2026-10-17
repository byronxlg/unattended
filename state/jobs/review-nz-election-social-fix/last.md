Verdict: **request changes**

1. **Important** - `product/nz_election/pipeline/social.py:155`: No runtime length guard exists. An offline probe with a 513-character base query still invoked the injected transport 24 times. Validate every fully composed query against `<= 512` before reserving credits or sending any paid request. Reject oversized queries with an allowlisted diagnostic code; add boundary tests proving zero requests for oversized input.

2. **Important** - `product/nz_election/pipeline/social.py:37`: Removing `"New Zealand First"` and `"Opportunity Party"` changes coverage: posts containing only those phrases no longer qualify. `"Opportunities Party"` also broadens the former `"The Opportunities Party"` match. Update the public method caption in `social_page.py:82` to disclose these coverage choices and their effect on party comparisons.

The eval’s arithmetic would catch the incident: an independent read-only probe measured **522 characters on main, 472 on HEAD**. The 512 bound matches the reported upstream rejection; the [endpoint documentation](https://docs.twitterapi.io/api-reference/endpoint/tweet_advanced_search) does not independently specify that limit.

No existing tests were changed or checks weakened. No new diagnostic leakage path found: logged values are allowlisted codes, bounded statuses and local indices. Full query provenance already persists in aggregates independently of diagnostics.

Requested verification was blocked by sandbox permissions:

- `evals/social-query-length/check.sh`
  ```text
  evals/social-query-length/check.sh: line 6: cannot create temp file for here document: Operation not permitted
  ```
- `uv run --with pytest pytest -q product/nz_election/tests/test_social_diagnostics.py product/nz_election/tests/test_social.py`
- `bin/lint`

  Both returned:
  ```text
  error: Failed to initialize cache at `/Users/byron/.cache/uv`
    Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
  ```

No files changed. Test and lint results remain unverified.