Fresh-context review of PR #117 (nz-election-settlement-prep), read-only. Worktree .worktrees/nz-election-settlement-prep,
branch change/nz-election-settlement-prep, base origin/main. Diff: git diff origin/main...HEAD -- product/
(pipeline/settlement_capture.py, runbook/night.md, tests/test_result_import.py). Judge against REVIEW.md.

Goal: a command that prepares the settled/official result capture deterministically from a pinned bundle so the
existing manual result-import workflow can apply it after 7 Nov, operable by Claude alone. Check: output is
deterministic (same bundle, same bytes); provenance (source URL, retrieved time, official vs preliminary) is carried,
never invented; bad or partial input fails closed with a named code and no raw upstream text in errors; the runbook
steps match the code and the import workflow; tests check behaviour, not markup. Supervisor host evidence:
pytest test_result_import.py test_result_states.py 92 passed incl. Chromium; Codex round-trip prep then import PASS night,
PASS waterfall.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.

Second review (PR #117 after fix-1 a971810): the first review found the synthetic-label guard scanned raw_xml, so real EC XML naming DemocracyNZ was refused. fix-1 limits the label scan to provenance and adds test_prepare_accepts_democracy_party_content. Check the fix and that nothing else regressed; review the full diff against origin/main.
