# Build: complete the deployed rehearsal contract (readiness-3 increment 1)

Page plan: intent/nz-election/pages/night.md (no page change in this job; the night page's harness is the subject).

## Goal
`product/nz_election/tests/night_deployed.py` (`--probe`, `--rehearse`, `--faults`) and `tests/night_live_browser.py`
must be able to demonstrate every 3 November instruction in `intent/nz-election/plan-m3.md` ("Browser-access probe and
rehearsal before 4 November"). Today they cannot (audit: `state/jobs/research-nz-election-readiness-3/last.md`, item 1):

1. CORS probing (night_deployed.py around :151) covers four files and no selected detail file.
2. The rehearsal (around :315) asserts no export, source-link or waterfall evidence.
3. The illustrative replay has zero leader changes: `pipeline/night.py` (around :74) scales final margins and keeps
   final leaders, so "leader changes" can never be observed.
4. The "reference retention" browser state (night_live_browser.py around :84) only triggers an HTTP 503; it never changes
   the reference set.

## Read first
`AGENTS.md`, `REVIEW.md`, the plan-m3 paragraphs named above, `product/nz_election/runbook/night.md` (rehearsal and faults
sections), the two test files, `pipeline/night.py`, `pipeline/night_live.py`, `web/night-live.mjs`.

## Constraints
- Keep three things separate and labelled: the historical replay (`2023-illustrative`, golden end 2,851,211 valid party
  votes, House 122, unchanged), the unmodified probe (ordinary CORS fetch, no interception), and synthetic fault/transition
  states (leader change, reference change). Synthetic states never feed the historical replay or its golden totals.
- Leader changes: add a separate synthetic sequence (or a clearly labelled fault state) in which at least one electorate
  leader changes between frames; the rehearsal asserts the page shows the change. Do not alter the 2023 replay's final.
- Reference transition: a synthetic state where the packaged reference set changes mid-session; assert the client keeps
  the last complete snapshot until the new set is complete (plan-m3 increment 5 rule), separately from the 503 case.
- Probe: include one selected `eNN/eNN.xml` detail URL in the CORS probe record.
- Rehearsal: assert local exports download and carry provenance, source links resolve on the page, and the waterfall
  module renders in populated states.
- No network in pytest; injected transport and clocks as the existing tests do. Main's tests at origin/main may move only
  where a contract named above moves; say which and why in last.md.

## Definition of done
- `uv run --with pytest pytest -q product/nz_election/tests/test_night*.py` passes on the host (Chromium tests may be
  skipped in your sandbox; say so).
- New tests fail on origin/main's versions of the two harness files (show the command and the failure lines).
- `uv run product/nz_election/pipeline/verify.py night` prints `PASS night`; `bin/lint` prints ok.
- `runbook/night.md` rehearsal section lists the new states and the exact commands for 3 and 6 November.
- Commit in the worktree; do not push. last.md: files, commands with output, what you could not run.
