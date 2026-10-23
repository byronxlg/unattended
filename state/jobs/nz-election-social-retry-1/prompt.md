# nz-election-social-retry-1: a retried window must not cost the whole day

Kind: build (pipeline only; no template, CSS or route change). Change: nz-election. Worktree
`.worktrees/nz-election-social-retry` on `change/nz-election-social-retry` from main 28279a5.

## What happened

NZ election social daily run 39966576709 (budget day 2026-10-24 NZ, sample day 2026-10-23,
code 6b21eea) reserved 7,560 credits, ran 2 h 10 min, and `collect` returned `limited=True`:
`FAIL social: SOCIAL_CREDIT_CAP`, nothing published, all 7,560 credits spent for no sample.
The ledger row for that run shows requests 24, spent 7560. Cause, read from the code:
`product/nz_election/pipeline/social.py:196-230`. The allocation is exactly 24 pages
(7,800 cap // 315 = 24) for 24 hourly windows, and every attempt, including a 429/5xx retry
(`continue` at about line 240), charges one request. One retry anywhere means the last window
cannot be fetched and the whole day is discarded at `refresh_social` (`if limited: error =
'SOCIAL_CREDIT_CAP'`). The run log printed no diagnostic, so which window retried is unknown.

## Goal

A day where some windows could not be fetched within the allocation still publishes the
windows that were fetched, honestly labelled; the credits are never spent for nothing.

Invariants (choose the data shape yourself, then keep every validator consistent with it):
- The cap is unchanged: 7,800 per budget day, reservation 315, never exceeded
  (`validate_ledger`, the reserve step, `collect`'s pre-request check).
- The day record still validates in `validate_record`/provenance checks
  (`social.py:410-431`, which today require exactly 24 windows matching `windows(day)`);
  a window that was not fetched must be distinguishable from one that returned zero posts.
- Aggregates only; the existing minimum-sample and withholding rules still apply to the
  partial sample; the 10 percent classification exclusion bound is computed on what was sent.
- Readers are told: the status message and the record carry how many of the 24 hours were
  sampled (for example "23 of 24 hours sampled"), through the existing caption/status code
  paths, no new markup.
- If no window was fetched, behaviour is as today (SOCIAL_CREDIT_CAP, previous data retained).
- `print_diagnostic` (or equivalent) logs which windows retried and their HTTP status, with no
  query text, keys or post content, so the next failure is readable from the Actions log.
- s197 freeze, budget-day rollover and spent-day exit-0 behaviour unchanged.

Contracts that move with this change: the social provenance/record shape and its tests;
tests on main at 28279a5 may change only where they pin the old all-or-nothing behaviour,
and nothing gets weaker. Say in last.md which ones moved and why.

## Eval

Add `evals/social-retry-budget/` in the style of `evals/social-model-rotation/`: an injected
transport that returns one 503 then 200 on window 5 and 200 elsewhere; on main it ends
SOCIAL_CREDIT_CAP with no record, on this branch it publishes a record for 23 of 24 hours
with the ledger at 7,560 spent. Show it failing on 28279a5 and passing on HEAD.

## Definition of done

- `uv run --with pytest pytest -q product/nz_election/tests` passes (report the count).
- The eval: FAIL on 28279a5, PASS on HEAD (paste both outputs).
- `uv run product/nz_election/pipeline/verify.py social` (or the repo's verify entry point for
  the social family) prints PASS.
- `bin/lint` exits 0.
- Commit in the worktree, do not push, do not commit last.md.
