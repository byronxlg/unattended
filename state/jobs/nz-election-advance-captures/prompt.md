# Build: successive 2026 advance captures pass CI without daily test edits

Change: nz-election (readiness-4 increment 1). Worktree `.worktrees/nz-election-advance-captures`, branch `change/nz-election-advance-captures` from origin/main. Commit there; do not push.

## Goal
The supervisor will add one new immutable transcribed EC advance capture per day from 28 Oct to 6 Nov (Claude-only after 7 Nov). Today each new capture breaks two tests: `product/nz_election/tests/test_contracts.py:20` pins the capture count (145) and `product/nz_election/tests/test_advance_2026.py:35` loads the newest capture but asserts the original two rows and acquisition time. Make adding a capture (file plus manifest entry) need no test edit, without weakening any check.

## Read first
- `AGENTS.md`, `product/nz_election/runbook/advance.md`
- `product/nz_election/tests/test_contracts.py`, `product/nz_election/tests/test_advance_2026.py`, other `test_advance*.py`
- `product/nz_election/fixtures/manifest.json` (2026 advance entry near line 1782), `product/nz_election/fixtures/ec-2026/advance-voting-2026-10-28.csv`
- `product/nz_election/pipeline/daily_sources.py` (how the daily picks the capture), `product/nz_election/tools/advance_preflight.py`

## Constraints
- This is a build round with explicit test maintenance authorized: the two assertions above move. Every exact regression check on the original 28 Oct capture stays exact (pin it by path, not "newest").
- The capture count contract becomes derived from the registered set (manifest entries vs files on disk, each file registered, each entry's sha256 and bytes match), not a literal.
- Add tests for: latest-capture selection across two successive captures (synthetic, under a temp dir or test fixture dir, never a fake file in `fixtures/ec-2026/`), a revision of an earlier day in a later capture, a missing day (gap keeps cumulative null), retention of older captures.
- `runbook/advance.md`: the exact daily supervisor steps (transcribe, `advance_preflight.py <csv> --kind daily --url ...`, manifest fields, `verify.py advance --require-year 2026`, the test command below, PR, then `gh workflow run nz-election-daily.yml --ref main`). Correct the documented preflight command (it currently omits `--kind daily` and fails).
- No product page or template change. No new dependency.

## Done when
`uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_contracts.py` passes, and a scratch check you describe in last.md shows that adding a well-formed third capture plus manifest entry (in a throwaway copy, then removed) keeps that command green with no test edit. `bin/lint` ok. last.md lists the moved assertions and why each is not weaker.
