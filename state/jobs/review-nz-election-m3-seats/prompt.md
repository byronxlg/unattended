Fresh-context review of nz-election-m3-seats (PR #62), read-only. Worktree .worktrees/nz-election-m3-seats,
branch change/nz-election-m3-seats, head 467512b on supervisor captures dfdabe5. The PR body (`gh pr view 62`) is
a claim to check. Diff: git diff main...467512b. Judge against REVIEW.md (question test in pass 4 first), the
accepted page plan intent/nz-election/pages/night.md (question 3: who leads in my electorate), plan-m3.md
increment 4, and the brief state/jobs/nz-election-m3-seats/prompt.md.

Check: (1) electorate leaders and margins come only from the EC detail XML shape captured in
product/nz_election/fixtures (dfdabe5), parsed identically in xml_parser.py and web/night-parser.mjs (parity test
is real, not tautological); (2) seat calculations are conservative and labelled as provisional, never present a
projection as a result, overhang and electorate-seat bounds respected; (3) zero-count and partial-count states
read correctly, no "not available" text (ABSENT_TEXT gate), the s197 freeze notice intact; (4) replay makes no
official feed request; (5) contracts moved with the registered set without weakening any check on main at its
base (every edited pre-existing test and verify check); (6) accessibility of the hex map and searchable table:
landmarks, headings, keyboard, a table equivalent for the map, target size; (7) runbook section true.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
