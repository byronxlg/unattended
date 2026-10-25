Committed `ca7bec1`, not pushed. Added shared sunsets, social deployment, post-election copy, tests, and runbook guidance.

```text
uv run --with pytest pytest -q
5 failed, 2612 passed, 2 errors in 735.24s (0:12:15)

uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS social
PASS home
PASS home-routes
PASS markets
PASS advance
PASS night
PASS waterfall
PASS campaign
PASS all

bin/lint
lint ok (990 text files)
```

All failures/errors were Chromium sandbox launch failures: night deployed probe/rehearse/faults, party picker, result states, and two night-page browser checks. Screenshots remain blocked; none were produced or inspected.

Exact cases, constant locations, and screenshot instructions are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-post-schedules/last.md), left uncommitted.