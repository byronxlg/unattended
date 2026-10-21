Fresh-context design review of nz-election-night-page, read-only. Worktree .worktrees/nz-election-night-page,
branch change/nz-election-night-page, head f02d0f4. PR #60 body (`gh pr view 60`) is a claim to check.
Diff: git diff main...f02d0f4. Judge against REVIEW.md (question test in pass 4 first), the accepted page plan
intent/nz-election/pages/night.md, plan-m3.md increment 2 (page half), and the brief
state/jobs/nz-election-night-page/prompt.md (main checkout).

Check: (1) the page answers the plan's questions in rank order in each state (before night, counting, final,
replay), above-the-fold content matches the plan at 390x844; (2) the replay is labelled as a replay everywhere it
shows, never readable as live or official, and makes no official feed request; (3) every number on the page comes
from the night family or snapshots with provenance, nothing invented, no "not available" text (ABSENT_TEXT gate);
(4) browser parser and Python parser agree (parity test tests what it claims); (5) the replay scheduler: start,
pause, end frame reached at every speed, no drift; (6) contracts moved with the registered set (80 routes) without
weakening any check on main at its base; (7) accessibility: landmarks, headings, target size, live region not
announced every tick, reduced motion; (8) style per design-principles.md and look-538.md, applied last.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
