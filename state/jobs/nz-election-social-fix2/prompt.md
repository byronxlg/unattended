# Fix round 1 on change/nz-election-social-fix2 (PR #28)

Same worktree, same branch, on top of 983f112. Commit here; never push. The fresh review (second
comment on PR #28, pasted below in full) found four Important items; items 1 to 3 are yours, item 4
is accepted by the supervisor with reasoning on the PR (no rows with the old key exist anywhere:
the data branch holds only social/credits.*; the validator stays strict). This is a fix round:
protected tests are the ones on main at the base commit eecc6fb (`git diff eecc6fb..HEAD --stat --
product/nz_election/tests` shows what this branch already moved; move nothing else there). Tests
this branch added (test_social_exclusions.py, and the lines 983f112 changed in test_social.py,
test_social_diagnostics.py, test_social_fix_round1.py) are yours and move with the fix.

## Item 1: decode failures stay fatal with their original code

Invariant: nothing weaker than main. A 200 whose body fails `decode()` (over MAX_BYTES, invalid
JSON, non-object JSON) is fatal as on main, with its original code (SOCIAL_RESPONSE_LIMIT or
SOCIAL_INVALID_RESPONSE), and the fatal line now also carries `check=decode`. Only the structural
checks after a successful decode (model, answers, type, probabilities, sum, choice, value) are
per-post exclusions. Reasoning: main would have printed SOCIAL_RESPONSE_LIMIT or
SOCIAL_INVALID_RESPONSE for a decode failure, and the incident printed
SOCIAL_CLASSIFICATION_FAILED, so the incident was a post-decode structural failure; a body that
does not decode is more likely an upstream outage than one odd post. Enforce where: `classify()`
in product/nz_election/pipeline/social.py. Verify: nine valid responses plus one oversized,
malformed or non-object response: the run fails, the stderr line names the original code and
`check=decode`, no row is written. Rewrite test_decode_failures_are_exclusions accordingly.

## Item 2: a successful classification batch leaves no stale failure state

Invariant: the code printed by the fatal line in refresh_social is the code of the failure that
stopped the run. After `classify()` returns with exclusions, `diagnostic['code']` and `check` must
not still say SOCIAL_CLASSIFICATION_FAILED; keep the last exclusion's context separately so that
the fatal line after the 10 percent bound trips still carries that exclusion's check and window
(as the review confirmed it does today). Verify: inject an aggregate failure after one exclusion
among ten posts: the fatal line reads SOCIAL_UPSTREAM_FAILED, not SOCIAL_CLASSIFICATION_FAILED;
and the bound-trip test still pins its line.

## Item 3: stop sending to Jev once the bound cannot be met

Invariant: no Jev request is made once failure is certain. Duplicate and unsupported posts are
decided without a Jev call, so the number of posts that will be sent is known before the first
request. Stop (fatal, SOCIAL_CLASSIFICATION_FAILED, with the last exclusion's check and window)
as soon as `excluded['classification'] * 10 > sent`. An isolated first failure still continues;
exactly 10 percent still passes; the final check in refresh_social may stay as a backstop.
Choose the shape. Verify: 480 invalid candidates make at most 49 Jev calls (pin the count with the
injected transport); the existing 9, 10, 11 sent cases still hold.

## Definition of done

- `evals/social-classify-exclusion/check.sh` last line: `PASS classify: 2 classified, 1 excluded, check named`
- `evals/social-query-length/check.sh` last line: `PASS query length 495 of 512`
- `uv run --with pytest pytest -q product/nz_election` passes
- `bin/lint` clean
- `uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/social-fixture --day 2026-10-16 --now 2026-10-17T03:00:00Z` prints `PASS social`
- `last.md`: per item, where it is enforced and the test that fails without it, outputs verbatim.
  Do not commit `last.md`.

## The fresh review, verbatim

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