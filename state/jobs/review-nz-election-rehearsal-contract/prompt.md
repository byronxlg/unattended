Fresh-context review of PR #95 (nz-election-rehearsal-contract), read-only. Worktree .worktrees/nz-election-rehearsal-contract,
branch change/nz-election-rehearsal-contract, head b4535af on base 497f3ff. Diff: git diff 497f3ff...b4535af.
Judge against REVIEW.md. Brief: state/jobs/nz-election-rehearsal-contract/prompt.md (goal items 1 to 4, constraints).

The change: night_deployed.py probes CORS on a selected detail file too; the rehearsal asserts export, source-link and
waterfall evidence; a separately labelled synthetic sequence gives leader changes and a reference-set change; the
reference-retention browser state now changes the reference set (fix-1 moved its baseline capture after screenshot cleanup).
Check: the historical replay (2023-illustrative, end 2,851,211 valid party votes, House 122) is untouched and no synthetic
state can feed it or its golden totals; the unmodified probe stays an ordinary CORS fetch with no interception; new
assertions would fail on the old harness (they are not vacuous); the whole-markup equality and renamed-not-shown checks
in night_live_browser.py were not weakened by the fix-1 reorder; no existing check on data, provenance, absence or
accessibility was loosened.
Supervisor host run: test_night*.py 259 passed incl. host Chromium; bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
