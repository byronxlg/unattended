# Social POC: a bad classification response excludes a post, names its check, and does not waste the day's credits

You are the engineer on the NZ election social proof of concept. Work in this worktree
(`.worktrees/nz-election-social-fix2`, branch `change/nz-election-social-fix2`, from main at
433b653 plus the eval commit 5071194). Commit here; never push. Read `AGENTS.md` first.

## What happened

The proving run of PR #25 (NZ election social daily, run 39042618322, budget day 2026-10-18 NZ)
collected 24 pages, spent the whole 7,560 credit reservation, then failed on the first
classification response:

    social diagnostic: SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=0 attempt=1

The response was HTTP 200 and failed one of the structural checks in `classify()`
(`product/nz_election/pipeline/social.py`), but every check there raises a bare `ValueError`, so
the log cannot say which. Twenty-four supervisor probes against the live upstream (emoji only,
URL only, mentions, te reo, 3000 characters, all caps, ambiguous party texts) all validated, so
the cause is unknown. The sample is never stored (that is a gate), so the post cannot be replayed.
Every run from now until this lands spends a day of credits for nothing.

Read first: `evals/social-classify-exclusion/task.md` and `check.sh` (the incident's eval),
`product/nz_election/pipeline/social.py` (`classify`, `diagnostic_code`, `DIAGNOSTIC_CODES`,
`refresh_social`, `aggregate`, the validator at `keys(sample['exclusions'], ...)`),
`product/nz_election/pipeline/social_page.py` (lines 81 and 90, the exclusion caption),
`product/nz_election/tests/test_social.py` (line 89 pins the exclusion dict),
`product/nz_election/tests/test_social_diagnostics.py` (pins the diagnostic line format),
`evals/social-query-length/task.md` (the previous incident, same shape of lesson).

## Invariants (name them in your commit message)

1. A classification response that fails validation excludes that one post. The exclusion is
   counted alongside `duplicate`, `unsupported` and `irrelevant`, flows through `aggregate`, the
   bundle validator, and the social/poc/ page caption ("Excluded: ..."), and the page's sample
   size stays honest. Choose the key name.
2. The run still fails with `SOCIAL_CLASSIFICATION_FAILED` when the excluded-for-classification
   count exceeds 10 percent of the posts sent for classification (so a broken upstream or a
   broken contract still stops the run, and a single odd post does not).
3. The diagnostic names the failed check with a fixed structural name from a small set you define
   (for example model, answers, type, probabilities, sum, choice, value, decode), stored in the
   diagnostic dict under the key `check` (the eval reads `diagnostic['check']`) and printed to
   stderr in the diagnostic line. Never a response body, post text, handle or key. The fatal
   line keeps its present shape for the present cases and gains the check name; the per-post
   exclusion prints one line per excluded post in the same shape.
4. The tie case is valid: `choice` may be any key whose probability equals the maximum, not only
   the first such key in mapping order. Decide whether the sum tolerance (.001) matches a
   two-decimal upstream (observed responses sum to exactly 1.00; keep the tolerance unless you can
   show it is wrong, and say so either way in `last.md`).
5. Nothing weaker: every existing structural check stays, the data gates stay (aggregates only,
   no raw posts), the credit ledger and the s197 freeze are untouched.

## Tests

This is a build round of the POC, not a fix: tests on main that pin the exclusion dict
(`test_social.py:89`) and the diagnostic line (`test_social_diagnostics.py`) move with the
registered set. Each changed assertion must still pin the full line or the full dict; add tests
for the per-post exclusion, the 10 percent bound (just under passes, just over fails), the tie,
and that the check name never carries post text. Use the injected transport like the existing
tests do.

## Definition of done

- `evals/social-classify-exclusion/check.sh` last line: `PASS classify: 2 classified, 1 excluded, check named`
- `evals/social-query-length/check.sh` last line: `PASS query length 495 of 512`
- `uv run --with pytest pytest -q product/nz_election` passes
- `bin/lint` clean
- `uv run product/nz_election/pipeline/social.py --fixtures --out /tmp/social-fixture` (or the
  documented offline verification command in `runbook/`) still passes and the rendered social
  page caption shows the new exclusion count; say which command in `last.md`
- `last.md`: what the diagnostic will now print for the incident's shape of failure, the
  exclusion key you chose, the decision on the sum tolerance, and the test outputs verbatim.
  Do not commit `last.md`.
