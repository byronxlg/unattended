**Verdict: request changes.**

- **Important: `product/nz_election/pipeline/social.py:140,175`**: Decode failures, including oversized bodies and non-object JSON, now become recoverable classification exclusions. Main failed immediately with `SOCIAL_RESPONSE_LIMIT` or `SOCIAL_INVALID_RESPONSE`; HEAD can publish when these failures stay within 10%. This weakens invariant 5 and loses the original diagnostic code. Verify a fix with nine valid responses plus one oversized, malformed or non-object response: each must remain fatal with its original code and `check=decode`.

- **Important: `product/nz_election/pipeline/social.py:309,502`**: Restoring the last exclusion leaves `code`, `check` and location populated after a successful classification batch. A subsequent aggregate exception is reported as that earlier classification failure because `diagnostic['code']` takes precedence. This violates invariant 3’s accurate diagnostics. Keep exclusion context separately and clear active failure state after accepting the bound. Verify by injecting an aggregate failure after one exclusion among ten posts. Final writes/publication occur outside this catch, so they do not inherit this particular misreport.

- **Important: `product/nz_election/pipeline/social.py:494`**: The bound runs only after every Jev request. An all-invalid 480-post sample makes **480 calls**, although failure is inevitable after 49 exclusions once the final eligible denominator is known. That is unacceptable avoidable spend for a daily run intended to survive upstream failures. Precompute the denominator after deduplication and unsupported filtering, then stop when recovery becomes impossible. Verify 49 calls for 480 invalid candidates while preserving isolated-first-failure and exactly-10% cases.

- **Important: `product/nz_election/pipeline/social.py:370`**: Existing rows containing only the original three exclusion keys now fail `INVALID_SOCIAL_FIELDS`. There is no compatibility handling before `refresh_social` validates the old bundle at line 453; the page also directly indexes the new key. If legacy rows exist, refresh and rendering are blocked. Verify a fix using a main-produced bundle through validation, refresh and rendering, preserving sample arithmetic. Live legacy-row presence remains unverified.

Other checks: the denominator correctly excludes duplicates and unsupported posts, includes irrelevant responses, and exactly 10% passes. The bound’s fatal line retains the last exclusion’s correct check/window. Ties are accepted and `.001` remains unchanged. Registered exclusions, arithmetic, caption, fixed check names and moved full-dict/full-line assertions are intact. No real post text, handles or credentials found in the added fixtures; HTTP and transport failures remain fatal.

Read-only verification used `.venv/bin/python -B -c` for in-memory probes and both evals’ embedded Python:
```text
PASS classify: 2 classified, 1 excluded, check named
PASS query length 495 of 512
PASS malformed structures main versus HEAD: 54
PASS transport exceptions remain fatal
```

Review limitations: PR body/comments could not be retrieved: `gh` connectivity failed and the connector requires reauthentication. Live-site retrieval also failed. Full pytest and `bin/lint` could not start because uv cache access was denied. No files changed.