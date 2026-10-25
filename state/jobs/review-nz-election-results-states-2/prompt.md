Second fresh-context review of PR #79 (nz-election-results-states), read-only. Worktree .worktrees/nz-election-results-states,
branch change/nz-election-results-states, head 84f8da5. Fix diff: git diff 739f880...84f8da5; whole change: git diff c2ce1fc...84f8da5.
Judge against REVIEW.md, pass 4 (the question test against intent/nz-election/pages/night.md) before any visual judgement.

The first review asked for: (1) the official state must not be reachable by relabelling preliminary data (dates and a label
only); (2) preliminary copy must not survive the handover to official; (3) the Q3 check must run with named leaders.
The fix's invariant is source provenance: an official package must name an official source URL distinct from the
preliminary feed and a source clock, parsed from the XML, on or after 27 November; otherwise it is refused.

Check: each of the three items is actually closed, not worded around; no path produces "official" from the preliminary
feed or from a hand-edited date; the source clock comes from parsed content, not file metadata or argv; the states still
only advance; nothing weakens an existing check; tests on main at c2ce1fc are untouched (the branch's own tests may move).
Host on 84f8da5: the seven Chromium tests (night_deployed browser x3, parties picker, result_states incl. browser, XML
parity, replay no-official-request) 48 passed; verify night and waterfall PASS; bin/lint ok. Codex: the provenance
regression fails on 739f880. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
