# Eval: one bad classification response excludes one post and names its failed check

Origin: production incident 2026-10-17T17:00Z. The proving run of PR #25 ("NZ election social
daily", run 39042618322, budget day 2026-10-18 NZ) collected 24 pages and spent the whole 7,560
credit reservation, then failed on the first classification response: `social diagnostic:
SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=0 attempt=1`. The response was HTTP
200 and failed one of the structural checks in classify(), but every check raises a bare
ValueError, so the log cannot say which. Twenty-four host probes against the live upstream with
synthetic texts (emoji, URLs, te reo, 3000 characters, ties) all passed, so the cause is
unknown and the day's credits were spent for nothing. The sample is never stored, so the post
cannot be replayed.

Invariant: a classification response that fails validation is a per-post exclusion, counted
and shown with the other exclusions, not a run failure, until the unclassified share exceeds a
bound; the diagnostic names the failed check by a fixed structural name, never a response body,
post text, handle or key. Tests on main pin the existing diagnostic line format and the
exclusion keys; they move with the registered set, nothing weaker.

Check: `evals/social-classify-exclusion/check.sh` classifies three posts through an injected
transport: a valid response, a valid response whose choice is a tied argmax key that is not the
first key in the mapping, and a response missing one question. Expected last line:
`PASS classify: 2 classified, 1 excluded, check named`.
