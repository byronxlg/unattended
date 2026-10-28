Fresh-context review of PR #119 (nz-election-backlog-nits), read-only. Worktree .worktrees/nz-election-backlog-nits,
branch change/nz-election-backlog-nits, base origin/main. Diff: git diff origin/main...HEAD -- product/
(pipeline/funding_page.py, pipeline/home_graphics.py, tests/test_design.py, tests/test_funding_totals.py). Judge against REVIEW.md.

Goal: funding/ and the home funding summary compute totals, rounding and return counts through one function, so the two
cannot disagree; test_design.py checks landmarks by parsing structure, not by matching markup strings.
Check: published amounts and counts unchanged on both routes (the label count and the hidden table count were return_count
and len before; are they still the same values?); bar widths from cents are correct; no test pins markup, classes or bytes;
the landmark test fails for a missing or duplicated landmark.
Supervisor host evidence: pytest -k 'funding or design or home_graphics' 86 passed incl. Chromium.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
