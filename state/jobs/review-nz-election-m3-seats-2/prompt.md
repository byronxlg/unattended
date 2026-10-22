Second fresh-context review of PR #62 (nz-election-m3-seats), read-only. Worktree .worktrees/nz-election-m3-seats,
branch change/nz-election-m3-seats, head ec9d3fb. Diff of the fix round: git diff 467512b..ec9d3fb; whole change:
git diff main...ec9d3fb. Judge against REVIEW.md and the first review's findings (gh pr view 62 --comments).

Check each first-review item is closed with a test that fails on 467512b: (1) the seven Maori electorates fit inside
the hex map viewBox (night_electorates.py), (2) a reported tie gives margin 0 and a named tie in both parsers
(xml_parser.py and night-parser.mjs, parity), (3) hex selection targets at least 24 px and the harness target check
covers the route, (4) runbook/night.md current. Then anything new the fix introduced. No check on main weakened.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
