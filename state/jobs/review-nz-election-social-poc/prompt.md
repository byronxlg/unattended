Fresh-context review of the social proof of concept, read-only. Worktree
.worktrees/nz-election-social-poc, branch change/nz-election-social-poc, three commits on top
of main 5c1fd99 (git diff main...HEAD; 17 files). PR #24. Judge it against REVIEW.md, every
pass, and against the brief in state/jobs/nz-election-social-poc/prompt.md plus followup-1.md
and followup-2.md (read them first: they are the contract). The engineer's own account is
.worktrees/nz-election-social-poc/last.md: a claim list to check, not evidence.

What this is: Byron's rule is "POC every new thing early and refine" (issue #22). This change
adds pipeline/social.py (collect through the X upstream, classify through the Jev upstream,
aggregate), a data/social family of aggregates, route social/poc/ labelled Proof of concept
with sample size and date range, a daily workflow nz-election-social-daily.yml at 13:40Z, a
runbook section, and tests with an injected transport. Route count moves 77 to 78 and the
contracts moved with the registered set.

Screenshots attached (--image) are from the host harness on 1271c0e: social/poc/ at 1280x800
and 390x844. The fixture has no social sample, so they show the empty state only.

Check specifically, in this order:
(1) Leaks: can any raw post text, handle, user id, post id, query string or key reach the
tree, data/, a page, a screenshot, a log line, an Actions step output or a PR body? Trace the
error paths too (an exception that prints the upstream response body is a leak). The
validator in social.py and test_validator_rejects_identifiers: what would get past them.
(2) The workflow: permissions, which steps see X_UPSTREAM_KEY and TYPESAFE_API_KEY, whether any
step could print its environment, what happens on a failed collection (previous data retained,
nothing published), the s197 freeze check at every stage, and whether workflow_dispatch with
the day input can be used for the first real day safely.
(3) The credit cap: 7,800 per day, reserved before every attempt including empty results and
retries, durable across runs, single use. Would a crash between reservation and spend
over-spend or under-count; can two runs on the same day exceed the cap.
(4) Contracts: every modified assertion in test_build.py, test_contracts.py, test_design.py,
test_electorates.py, test_verify_supplied.py, screenshots.py: is anything weaker than on main,
or is the registered set the single source the count derives from.
(5) The page: does the caption say Proof of concept, the sample size, the date range and the
method honestly in the populated state (read social_page.py; the screenshot shows only the
empty state); is "unavailable" copy true; does the source note follow the design grammar
(div.source-note, links in p.source-actions).
(6) Anything that changes the live site's existing routes, data families or workflows beyond
the one new route and family.

Report: findings labelled Important or Nit with file:line, then one paragraph on the page copy
and screenshots, then a last line "Important findings: N". No emojis, no em dashes.
