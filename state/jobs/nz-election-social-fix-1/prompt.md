# Fix: social daily fails on every request (query over the upstream limit) and hides why

Read `AGENTS.md` first. You are in `.worktrees/nz-election-social-fix` on branch
`change/nz-election-social-fix` from main (bf36447, which includes PR #24, the social POC).
Commit here; do not push; do not commit `last.md`.

## What happened

The first real run of "NZ election social daily" (run 38998322076, sample day 2026-10-16) failed
on its first paid request, under one second in. The supervisor reproduced it: api.twitterapi.io
answers HTTP 400 with `{"detail":"query is too long (522 characters). The maximum length is 512
characters; longer queries return no results. Please split it into multiple shorter queries"}`.
`QUERY` in `product/nz_election/pipeline/social.py` is 477 characters and every hourly window
appends ` since_time:<10 digits> until_time:<10 digits>` (45 characters). A 296 character
variant of the same query returned 200 with tweets and `has_next_page`, so the endpoint, the
epoch operators, `queryType=Latest` and the key are fine.

The Actions log said only `FAIL social: SOCIAL_UPSTREAM_FAILED`. `refresh_social` catches every
exception into that one code and `transport` discards the HTTP status, so the log cannot tell a
rejected query from a bad key or a network failure.

## Read first

- `product/nz_election/pipeline/social.py`: `QUERY` (line 32), `transport`, `collect`,
  `refresh_social` (the `except Exception` near line 416), `main`.
- `product/nz_election/tests/test_social.py`, `test_social_fix_round1.py`,
  `test_social_fix_round2.py`: the contracts; `test_social.py:82` checks the suffix operators;
  the round1 and round2 tests pin `SOCIAL_UPSTREAM_FAILED` as the status row's `error_code`.
- `intent/nz-election/social.md` lines 11 to 30: where the query came from.
- `evals/social-query-length/`: the eval for this incident, already on this branch.

## Two items

1. Query length. Invariant: every query string sent to advanced_search, suffix included, is at
   most 512 characters; the upstream enforces it with a 400. Shorten `QUERY` so the longest
   hourly query of any day stays under the limit with room to spare (aim for 490 or less in
   total). Keep the three hashtags, every leader named in the leader mapping and every party;
   which spelling variants or the trailing National/Labour/Greens clause give way is your call,
   and say why in the commit message. Add a unit test that composes the query the way `collect`
   does with real `windows()` output and asserts the bound. Update the query block in
   `intent/nz-election/social.md` to what ships. No day has data from the old query, so no
   method version bump is needed; say so in the commit message. If you factor the query
   composition into a function, point `evals/social-query-length/check.sh` at it.

2. Diagnostics. Invariant: a failed collection leaves a diagnosable line on stderr naming the
   inner error code (`SOCIAL_COLLECTION_FAILED`, `SOCIAL_TRANSPORT_FAILED`,
   `SOCIAL_INVALID_PAGE`, `SOCIAL_CLASSIFICATION_FAILED`, and so on), the HTTP status when there
   was one, the window index and the attempt; never a response body, post text, handle or key.
   `transport` keeps discarding bodies on error; the status code is ours to surface. The status
   row's `error_code` and the `FAIL social: SOCIAL_UPSTREAM_FAILED` exit text stay as the tests
   pin them; the detail is an additional stderr line. Add a test with an injected `send` that
   returns 400 and asserts the stderr line carries the inner code and the status (capsys).

## Constraints

- Existing tests and assertions stay as they are; add tests, never weaken one.
- No network, no keys. The hourly loop, the ledger and the checkpoint logic do not change.
- No emojis, no em dashes. Humble commit messages.

## Definition of done

- `uv run --with pytest pytest -q product/nz_election/tests` passes (342 before plus yours).
- `evals/social-query-length/check.sh` last line `PASS query length <n> of 512` with n at most 490.
- `evals/pages-verify-polls-only/check.sh` last line `PASS all`.
- `bin/lint` prints ok.
- One or two commits on this branch; `last.md` says the measured query length, the test counts
  and the exact output lines of the four commands above.
