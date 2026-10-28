# Build: executable official-results capture and preflight (nz-election-official-capture)

Goal: on or after 27 Nov NZ, Claude alone must turn the EC's official results into the reviewed capture
`result-import/2026-11-27-official.json` that `nz-election-result-import.yml -f state=official` consumes. The runbook
(`product/nz_election/runbook/night.md` around lines 445-560) describes the capture's schema but there is no command
that produces it; `pipeline/fetch.py:146` (`night_xml`) accepts only preliminary/demo roots and stops after 8 Nov, so
it cannot be reused. Give Claude one operator-invoked command that acquires and preflights it.

Read first: `AGENTS.md`; `runbook/night.md` (settled and official sections, the import dispatch); `pipeline/fetch.py`;
`pipeline/result_states.py` (official path and its checks); `pipeline/result_import.py`;
`tools/settlement_capture.py` (the settlement prep command, follow its shape and error handling: named error codes,
no raw input echoed); `tests/test_result_import.py`, `tests/test_settlement_capture.py`, `tests/test_result_states.py`.

What the command does (you choose the shape and name, under `product/nz_election/tools/`):
- serial, complete acquisition of the official root and all 71 detail files from a base URL given on the command line
  (the configured official URL is an inference to confirm against the EC; the URL is an explicit argument, never
  guessed; reference drift versus the pinned settled baseline is a named failure needing explicit approval, not a
  mapping guess);
- immutable provenance per file (URL, retrieved_at UTC, sha256, `acquisition_source.kind: "official"`);
- writes the capture and a manifest draft into an output directory, never into the registered manifest itself;
- compatibility check against the pinned settled baseline (same references, 71 electorates, totals consistent) and
  runs the existing official-state validation so a PASS means `result_states.py official` will accept it;
- refuses before 27 Nov 2026 NZDT by the same clock rule the official path uses (do not move it).

Constraints:
- Tests use injected transport only; no network. Synthetic fixtures are labelled synthetic.
- Tests on main at 1d1d9fa stay untouched; new tests in a new file.
- Runbook: edit only the settled/official section of `runbook/night.md` (another job edits the night-live
  watchdog section): replace the "separately acquired" gap with the exact command, its PASS line, and the review
  step before registering. Also fix the path mismatch there: the official example reads `artifacts/settled-data`
  while the fixture generator writes `artifacts/result-states/settled-data`; make the commands copy-pasteable.

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests/test_official_capture.py product/nz_election/tests/test_result_import.py product/nz_election/tests/test_result_states.py product/nz_election/tests/test_settlement_capture.py`
  passes (report counts; adjust the new file name if you name it otherwise), including: complete fixture PASS and
  accepted by the official path; missing detail file, checksum mismatch, reference drift, before-27-Nov clock and a
  non-official kind each fail with a named code and no raw input echoed.
- `bin/lint` passes.
- Commit on this branch; do not push. last.md lists the command, the PASS line, and the files changed.
