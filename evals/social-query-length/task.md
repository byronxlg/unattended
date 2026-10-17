# Eval: the social search query fits the upstream's 512 character limit

Origin: production incident 2026-10-17T03:19Z. The first real run of "NZ election social daily"
(run 38998322076, sample day 2026-10-16) failed on its first paid request. api.twitterapi.io
answered HTTP 400: query is too long (522 characters), the maximum length is 512. The query
shipped in PR #24 came verbatim from intent/nz-election/social.md and is 477 characters before
the `since_time:<epoch> until_time:<epoch>` suffix that every hourly window adds. The run's log
said only `FAIL social: SOCIAL_UPSTREAM_FAILED`; the HTTP status and the inner error code were
swallowed, so the cause took a supervisor reproduction to find.

Invariant: every query string sent to advanced_search, suffix included, is at most 512
characters; a failed collection names its inner error code and HTTP status in the log, never a
response body, post text, handle or key.

Check: `evals/social-query-length/check.sh` composes every hourly query of a sample day the way
collect() does and measures the longest. Expected last line: `PASS query length <n> of 512`.
