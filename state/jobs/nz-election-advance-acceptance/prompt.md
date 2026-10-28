# Build: advance capture publication acceptance

Change: nz-election. Worktree .worktrees/nz-election-advance-acceptance, branch change/nz-election-advance-acceptance, from origin/main. Commit there; never push.

## Goal
The supervisor hand-transcribes the EC advance vote count daily (28 Oct to 6 Nov), registers each capture in
product/nz_election/fixtures/manifest.json, and the daily workflow publishes it. Nothing today proves the reviewed
capture reached the release: `verify.py` (pipeline/verify.py around line 320) accepts a bundle without advance data,
and `--require-year` checks registered source captures, not what was published. Add an explicit acceptance check:
given a release bundle (and optionally the built site), the published advance family matches the newest registered
2026 capture (its sha256 or its latest observation date and cumulative count), and the rendered home and vote/ pages
show that count and date.

## Read first
AGENTS.md; product/nz_election/pipeline/verify.py; product/nz_election/tools/harden.py and bin/nz-election-harden;
product/nz_election/pipeline/vote_page.py (line 55 renders the count) and home.py (line 438 calls it);
product/nz_election/pipeline/daily_sources.py (line 82, daily reads committed captures); the 2026 advance entry in
fixtures/manifest.json (advance={year:2026,kind:"daily",...}); tests/test_advance*.py; runbook/nz-election.md.

## Constraints
- A new verify subcommand or option (your choice of shape) that the harden gate can call with
  `--require advance` or equivalent; default harden behaviour for other families unchanged.
- Fail codes are named and stable (for example ADVANCE_NOT_PUBLISHED, ADVANCE_STALE, ADVANCE_RENDER_MISMATCH);
  error text never echoes raw file content.
- A genuine missing EC day stays missing: a gap that makes the cumulative null hides the count by design and the
  check must not demand a number that was never published by the EC; it reports that state distinctly.
- New tests only; existing tests on origin/main stay as they are, except contracts that move with a newly registered
  subcommand or code (say which in last.md).
- Runbook: one short section in runbook/nz-election.md with the exact command the supervisor runs after each daily.

## Definition of done
- `uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py product/nz_election/tests/test_harden*.py`
  passes, and the new tests fail against origin/main's verify.py (show it).
- Cases proven: published capture omitted fails; older capture published fails; matching capture passes on both
  home and vote/; missing-day gap reported as its own state, not a pass with a number.
- `bin/lint` prints `lint ok`.
- last.md: files changed, the commands and their outputs, the runbook command.
