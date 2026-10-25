# Build: advance-voting capture preflight and a 2026 acceptance check (pipeline only, no page change)

Change: nz-election (schedule.md "26 Oct: advance voting"; readiness audit research-nz-election-readiness, item 3).
Read first: `AGENTS.md`, `intent/nz-election/plan-m3.md` (increment 1), `product/nz_election/pipeline/advance.py`,
`product/nz_election/pipeline/verify.py` (the advance check near line 314), `product/nz_election/fixtures/manifest.json`
(the 2023 advance entry near line 1466), `product/nz_election/tests/test_advance.py`.

## Problem
The supervisor will capture the 2026 EC advance-voting file by hand from 27 Oct NZ. Today
`advance.load()` returns `None` in production and `verify.py advance` passes on the 2023 fixture alone,
so a missing or malformed 2026 capture would pass unseen.

## Goal
1. `product/nz_election/tools/advance_preflight.py <csv> --url <url> [--archive-url <url>]`: read-only;
   reads a candidate file, reports detected header names, date and count columns, kind (daily or
   cumulative, inferred and stated as an inference), row count, first and last date, gaps, SHA-256,
   and prints the exact manifest entry (fields as the 2023 entry plus
   `advance: {year: 2026, kind, start: "2026-10-26", date_column, count_column}`) for the supervisor
   to review. It writes nothing. Malformed input exits nonzero with the existing `INVALID_ADVANCE` code.
2. `verify.py advance --require-year 2026` (or the existing `--require` mechanism if it fits) fails with a
   named code when no 2026 capture is registered; without the flag behaviour is unchanged.
3. Semantics held by tests: the newest registered capture replaces the whole series; missing dates are
   gaps, never zeros; a replacement capture with fewer days than the previous one is rejected or flagged
   with a named code (choose, and say which).
4. Operator recipe in a new file `product/nz_election/runbook/advance.md` (do not edit `runbook.md` or
   `runbook/night.md`; an open PR changes them): capture, preflight, fixture path, manifest entry, review, commit, verify.

## Constraints
Tests on main at the base sha are protected; the branch's own tests move with it. No network in tests;
fixtures for 2026 are synthetic and live under the tests' fixture dir, never registered as a production capture.

## Done
- `uv run --with pytest pytest -q product/nz_election/tests/test_advance.py` passes, new tests for
  preflight output, the require-year failure, gap semantics and the shorter replacement; at least one fails on the base sha.
- `uv run product/nz_election/pipeline/verify.py advance` prints PASS as before; with the require flag it fails with the named code.
- `bin/lint` ok. Commit in the worktree; summary lists files, tests, command output lines.
