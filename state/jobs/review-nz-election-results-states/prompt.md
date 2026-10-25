Fresh-context review of PR #79 (nz-election-results-states), read-only. Worktree .worktrees/nz-election-results-states,
branch change/nz-election-results-states, head 739f880. Diff: git diff c2ce1fc...739f880. Judge against REVIEW.md,
pass 4 (the question test against intent/nz-election/pages/night.md) before any visual judgement.

The change adds preliminary, settled and official result states (plan-week-after increment 2): a pinned preliminary
baseline, an official capture/package path, settled-state freshness, the home and night/ handover, evidence-only specials.

Check in particular: a state can only advance (preliminary to settled to official), never regress on a stale or partial
feed; the official state needs dated official evidence and cannot be produced by relabelling preliminary data; no copy
calls final-minus-preliminary "special votes" without evidence; the client stops polling in terminal states; absent
feeds render absence by the absent-text rule, never "not available"; tests exercise each transition boundary and nothing
weakens an existing check. Host: whole suite 2507 passed on 739f880; result_states_browser.py PASS 8 images; bin/lint ok.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
