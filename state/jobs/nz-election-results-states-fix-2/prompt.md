# Fix 2 on PR #79 (results-states), same branch, same thread

Second fresh review of 84f8da5 found one Important item:

1. Official (and settled) handover leaves the night/ navigation link labelled "Live preliminary results".
   The nav is generated outside the replaced snapshot at `product/nz_election/pipeline/night_page.py:106`
   (`<nav aria-label="Packaged results">`), and `web/night-live.mjs:67-68` only removes
   `#night-result-status` on handover. After a pack with mode other than live renders, no reader-visible
   text on night/ may still say "Live preliminary results" (nav label included). Choose the shape:
   update the label from `pack.mode` in `render`, or give the nav a neutral label; keep the
   `?sequence=` hrefs working.

Invariant and where it is enforced: the handover assertion in this branch's own browser/handover test
(test_result_states.py or night browser tests added on this branch) must be extended so it fails on
84f8da5: after settled and after official handover, `document.body.innerText` contains no
"Live preliminary results". Tests on main at c2ce1fc stay as they are, except the capture-count pin in
test_contracts.py which this branch already moved with its two registered captures (accepted).

Done when, in this worktree:
- `uv run --with pytest pytest -q product/nz_election/tests/test_result_states.py product/nz_election/tests/test_night_page.py product/nz_election/tests/test_night_operation.py` passes (host Chromium may be missing in your sandbox; say so if the browser tests skip).
- the extended assertion fails with web/night-live.mjs and night_page.py at 84f8da5 (show the command and output).
- `bin/lint` ok from the repo root if reachable.
Commit on change/nz-election-results-states; do not push; do not commit last.md or artifacts/.
