Fresh-context review of PR #114 (nz-election-advance-2026), read-only. Worktree .worktrees/nz-election-advance-2026,
branch change/nz-election-advance-2026, base origin/main. Product diff: git diff origin/main...HEAD -- product/
(fixtures/ec-2026/advance-voting-2026-10-28.csv, manifest.json, pipeline/advance.py, export.py, home.py, vote_page.py,
tools/advance_preflight.py, tests/test_advance.py, tests/test_advance_2026.py). Judge against REVIEW.md; page plans
intent/nz-election/pages/vote.md and pages/home.md.

Check: the transcribed capture matches its stated source (EC vote.nz voting statistics; 26 Oct 69,034, 27 Oct 106,714,
cumulative 175,748) and its provenance (url, retrieved time, caveat that it was transcribed by hand) is shown with the
figure; the line is absent rather than wrong when the family is missing, partial or not 2026; the preflight declared
kind cannot override a contradicting header; the moved assertion in test_advance.py only drops the "no 2026 capture"
assumption and weakens nothing else. Supervisor host evidence: pytest -k "advance or vote or home" 478 passed incl.
Chromium; origin/data build PASS 82 routes.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
