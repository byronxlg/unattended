Fresh-context review of PR #97 (nz-election-hexmap), read-only. Worktree .worktrees/nz-election-hexmap, branch
change/nz-election-hexmap, head e579ec6. Diff: git diff origin/main...e579ec6 (home_graphics.py, snapshots/hexmap.json,
tests/test_home_hexmap.py). Judge against REVIEW.md. Brief: state/jobs/nz-election-hexmap/prompt.md; page plan
intent/nz-election/pages/home.md; design product/nz_election/DESIGN.md.

Check: every one of the 71 electorates has exactly one cell and no two cells overlap; per-record provenance (source URL,
licence, retrieval time) is preserved; the snapshot loader's validation is not loosened; labels and focus targets stay
accessible at 390; no test pins markup, class names or bytes. Supervisor looked at the home map at 390 and 1280 on the
fixture build (islands recognisable, no overlap, no sideways scroll; one empty cell in the central North Island).
Supervisor host run with Chromium: test_snapshots*, test_home*, test_design 178 passed. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
