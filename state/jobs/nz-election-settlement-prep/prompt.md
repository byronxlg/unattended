# Build: deterministic settlement-capture preparation command

Change: nz-election (readiness-4 increment 2). Worktree `.worktrees/nz-election-settlement-prep`, branch `change/nz-election-settlement-prep` from origin/main. Commit there; do not push.

## Goal
After 8 Nov 06:00Z the operator (Claude alone, Codex gone) settles the last complete preliminary capture. `product/nz_election/runbook/night.md:469` requires an operator-created, reviewed capture that matches the pinned live row exactly, and `product/nz_election/pipeline/result_import.py:104` enforces that equality. Hand-building that capture on the night is the risk. Add a command beside `result_import.py` that prepares it deterministically from a pinned preliminary bundle.

## Read first
- `AGENTS.md`, `product/nz_election/runbook/night.md` (settlement and import sections from line 410)
- `product/nz_election/pipeline/result_import.py`, `product/nz_election/pipeline/result_states.py`, the result-import workflow under `.github/workflows/`
- `product/nz_election/tests/test_result_import.py`

## Constraints
- The helper extracts `raw_xml` into `raw`, preserves `retrieved_at` and `acquisition_source` byte for byte, writes nothing outside the output path it is given, and prints draft manifest metadata (path, sha256, bytes, retrieved_at, source) for the operator to review. It never fabricates a capture: refuse synthetic, demo or replay-labelled input, and input that is not a complete preliminary snapshot.
- Do not rebuild result states or change the import's equality check. Existing tests on main are not edited; add new tests in `test_result_import.py` or a new file.
- Runbook: replace the hand steps in night.md with the command, its output, and what the operator checks before running the import.
- No product page change. No new dependency.

## Done when
`uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py product/nz_election/tests/test_result_states.py` passes, including a round trip: pinned preliminary bundle, then prepare, then the existing settlement import, with `python3 -B product/nz_election/pipeline/verify.py night` and `verify.py waterfall` PASS on the result and counts and provenance unchanged; and rejection cases for a mismatched row and a synthetic or demo input. `bin/lint` ok. last.md lists the commands run and their output lines.
