Build M3 increment 1: advance voting, live before advance voting opens on 26 October.

Read first: intent/nz-election/plan-m3.md (decisions, then "Shared implementation contract",
"Increment 1" and "Increment 1 proof"), intent/nz-election/spec.md requirement 11 and 14,
intent/nz-election/design-principles.md, product/nz_election/AGENTS.md, REVIEW.md.

Worktree .worktrees/nz-election-m3-advance, branch change/nz-election-m3-advance from main. Commit
there, never push.

Scope: the files plan-m3.md names for increment 1. Fetch the 2023 historical advance-voting CSV
(https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/AdvanceVoteCSV,
or the CSV the official 2023 voting-statistics page links if that path moved) into the fixtures
with every manifest field (URL, archive URL if any, acquisition time, SHA-256, licence, notes);
record the actual URL you fetched. Do not invent a 2026 URL: discover it from the official
voting-statistics page if it exists yet, else record the source gate as unmet in last.md. The
production build omits the advance module until real 2026 data exists; historical data appears
only in labelled verification builds. Never render "not available", "Not reported" or an empty
heading; the existing visible-text gate must pass.

Contracts that move with the registered set: adding the advance family and the /campaign/ route
(if the plan's campaign page is a new route) changes route counts and family unions pinned in
tests/test_contracts.py, tests/screenshots.py and similar; update those pins to the new set,
nothing weaker. Do not edit home.py, home_charts.py, electorate_pages.py or their templates.

Definition of done, with outputs in last.md:
- `uv run --with pytest pytest -q product/nz_election` all pass (state the count).
- `uv run product/nz_election/pipeline/verify.py advance` prints exactly `PASS advance`.
- `uv run product/nz_election/pipeline/verify.py all ...` (as main's runbook runs it) prints `PASS all`.
- `bin/lint` prints lint ok.
- The plan's six named tests exist and pass; name one that fails on main's code.
- A populated verification build (historical 2023 series) and a production-like build (no 2026
  data, module absent) under /tmp/m3-advance/, with the exact commands. Chromium may be blocked
  in your sandbox: if so, say so; the supervisor runs the screenshot harness on the host (both
  builds must pass `product/nz_election/tests/screenshots.py --site <dir>`, including
  SMALL_TARGET, MISSING_SOURCE, PAGE_OVERFLOW and AXE checks at 360, 390 and 1280).
- last.md stays uncommitted.
