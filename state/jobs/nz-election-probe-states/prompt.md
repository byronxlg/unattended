# Build: the deployed night probe accepts healthy post-stop states

No page change; test harness only. Look: product/nz_election/DESIGN.md (unchanged).

## Goal

`product/nz_election/tests/night_deployed.py` is the deployed probe we run on election night and
the week after. At :318 it requires a live JSON response on night/ for ever after polls close, but
`web/night-live.mjs:28` stops polling by design at the shared cutoff (`pipeline/sunsets.py`) or on
a terminal result state. Research (state/jobs/research-nz-election-readiness-9/last.md) ran it in
memory: `night-data-transport=FAIL` at 8 Nov 06:01Z, 14 Nov 00:00Z and 27 Nov 00:00Z with retained
results and zero polling, and the empty shell fails the archive-only fallback predicate at :284.
After the cut (7 Nov afternoon) the supervisor runs this probe alone; a false FAIL on a healthy
site costs a night of investigation.

## Invariants

- The probe classifies the page state from what the page and its data say (waiting, live,
  stopped, settled, official; `pipeline/result_states.py` names them) and the clock from
  `sunsets.py`; no new literal timestamps.
- During the live window the transport requirement is unchanged (a live response is required;
  a missing one still fails).
- After the stop: PASS needs retained results visible (or the documented empty-shell wording when
  nothing was captured) and no live polling request; a poll request after the stop is a FAIL.
- The dated-fallback invariant at :284 stays; extend it to accept the empty shell only where the
  page states nothing was captured.

## Read first

`tests/night_deployed.py` (whole), `web/night-live.mjs`, `pipeline/sunsets.py`,
`pipeline/result_states.py`, `tests/test_night_deployed.py`, `runbook/night.md` probe section.

## Tests

Executable cases in `tests/test_night_deployed.py` at 7 Nov 08:00Z (live), 8 Nov 06:01Z,
14 Nov 00:00Z, 27 Nov 00:00Z, each healthy and each with one fault (polling after stop; retained
results missing). Tests on main at the base sha are protected; the branch's own tests move with it.
The healthy post-stop cases must fail on origin/main's night_deployed.py.

## Done

`uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py product/nz_election/tests/test_night_operation.py` 0 failed (includes Chromium cases; if the sandbox denies Chromium, say which cases did not run);
`bin/lint` ok. Commit in the worktree; do not push. last.md: files, the cases that fail on base.
