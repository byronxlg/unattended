Fresh-context review of PR #98 (nz-election-electorate-design), read-only. Worktree .worktrees/nz-election-electorate-design,
branch change/nz-election-electorate-design, head e647444 (1a23dc1 plus a supervisor merge of origin/main). Diff:
git diff origin/main...e647444. Judge against REVIEW.md. Brief: state/jobs/nz-election-electorate-design/prompt.md; page plan
intent/nz-election/pages/electorate.md; design product/nz_election/DESIGN.md.

Check: the merge resolution in pipeline/home_graphics.py hex_map keeps home (links), night (night=True, no links, source id)
and electorate (selected=) modes each correct; build.py heading set (electorate detail pages and night/ render their own h1);
candidate portraits carry licence and source; enrolment and Policy.nz links only when sourced; absent data is absent, not
"not available"; keyboard focus on the highlighted seat; no test pins markup, class names or bytes; edits to tests on main
are justified by the registered contract moving. Supervisor looked at Nelson, Waiariki, Epsom at 390 and 1280 on an
origin/data build (no sideways scroll). Host Chromium after the merge: 441 passed. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
