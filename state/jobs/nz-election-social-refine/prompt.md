# nz-election-social-refine: clean exit on a spent budget day, status message with no prior sample

Pipeline only (product/nz_election/pipeline/social.py and its tests, plus the daily workflow if the exit path needs it). No templates, no page markup, no styling: the page-facing caption nits wait for the social page plan.

## Goal

Two defects seen on real runs of `.github/workflows/nz-election-social-daily.yml`:

1. A run on a budget day that is already spent (the 16:50Z 2026-10-18 run after the day's 7,560 credits were used) stops with `SOCIAL_CREDIT_CAP` and the workflow goes red. That is the designed outcome, not a failure: the run should exit 0, publish nothing new, leave the previous data and credit ledger untouched, and write a status row that says the day's cap was already spent. A cap reached part-way through a run that did spend (a real collection that ran out) keeps today's behaviour; say in last.md which branch you chose for each case and why. Failures that are failures (transport, decode, classification, query length) stay fatal with their original codes.
2. `social.py:487-488`: with no earlier published day the status message reads "Collection limit reached; showing data through no previous data". Write a message that is true when there is no earlier sample (for example "Collection limit reached; no earlier sample is published.") and keep the existing wording when there is one.

## Read first

`AGENTS.md`, `product/nz_election/pipeline/social.py` (reservation, budget day, status, error paths around 420-530), `product/nz_election/tests/test_social.py` (lines 115-140 pin the cap behaviour), `product/nz_election/pipeline/verify.py:215-225` (the offline social rerun check), the social section of `runbook/`, `evals/social-*`.

## Constraints

- This is a build round, not a fix: tests on main that pin the old exit for the already-spent case (test_social.py around 121 and 133, verify.py:220) move with the new contract, and only for that case; nothing else in them weakens. Add tests for: spent day exits 0 with no transport call and no ledger change; no-prior-data message; mid-run cap unchanged.
- No raw posts, handles or keys anywhere; no live network in tests (injected transport as now).
- Update the runbook's social section in a line or two.
- Commit in the worktree; do not push. Do not commit last.md.

## Done when

- `uv run --with pytest pytest -q product` passes (report the count).
- `bin/lint` prints `lint ok`.
- `PYTHONPATH=. uv run python -m product.nz_election.pipeline.verify all` (or the repo's documented verify command if that differs) prints PASS for social.
- last.md lists the files changed, the tests that moved and why, and the exact commands with their output lines.
