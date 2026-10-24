# Build: deployed night probe and rehearsal harness (M3 Fri 30 Oct and Fri 6 Nov acceptance)

Page plan: intent/nz-election/pages/night.md (no page change in this job; the harness exercises the live /night/ route)

## Goal

The night client is built and tested locally, but nothing records it working on the deployed site.
Add one Playwright script that drives the real deployed `/night/` page and writes a dated,
machine-readable acceptance record. Two modes:

- `--probe`: the browser-access probe in `intent/nz-election/plan-m3.md` ("Browser-access probe and
  rehearsal before 4 November"), adjusted for the transport amendment: the browser reads only
  same-origin packaged JSON. Record (a) every same-origin night data request the page makes, status,
  and whether its body parses and validates with the existing night validators; (b) an ordinary
  in-page `fetch` (CORS mode, credentials omitted, no custom headers) to the 2026 feed root
  `https://media.election.net.nz/xml/` national files, recording the CORS failure or success as
  evidence (expected failure; that is why transport is Actions); (c) the dated fallback state the
  page presents when no live cycle exists. No request interception, no disabled security, no
  `no-cors`, no proxy in this mode.
- `--rehearse --speed 60`: open `/night/?sequence=2023-illustrative`, confirm the persistent label
  and initially paused state, select 60x, run to completion in real elapsed time, pause, resume,
  reset, and compare the final figures with the golden result (2,851,211 valid party votes, House
  122). Record wall-clock per phase, any official-feed requests (there must be none), console
  errors, and screenshots at 390x844 and 1280x800 of start, middle and end. Also select each
  archive (2017, 2020, 2023) and confirm it renders as a Final snapshot.
- Fault injection (route interception making the packaged JSON fail or go stale) is a third,
  separately named mode `--faults`, never mixed into `--probe`; it checks the page keeps the last
  good snapshot and shows the stale marker.

Every mode writes `artifacts/nz-election/deployed/<mode>-<UTC stamp>/record.json` (origin, URL list,
browser and version, start/end UTC, deployed code SHA if the page exposes build provenance, data
SHA if exposed, per-check PASS/FAIL with reason, screenshot paths) and prints `PASS deployed-<mode>`
or `FAIL deployed-<mode>: <check>` as its last line, exit code matching.

## Read first

- `intent/nz-election/plan-m3.md` (increment 5, transport amendment, browser-access probe section)
- `product/nz_election/runbook/night.md`
- `product/nz_election/tests/night_browser.py`, `night_live_browser.py`, `night_smoke.py` (reuse
  selectors and validators; do not duplicate parsing logic)
- `product/nz_election/web/night-live.mjs`, the night template

## Constraints

- New file `product/nz_election/tests/night_deployed.py`; edit `product/nz_election/runbook/night.md`
  (a "Deployed acceptance" section with the three commands and how to read the record; also fix the
  stale text that says live operation is future work). Do not edit `runbook/nz-election.md`,
  `verify.py`, `bin/`, `.github/`, or any page/template/web file; another job owns those files.
- `--origin` defaults to `https://byronxlg.com` with path prefix `/unattended/nz-election/`; allow
  `--base-url` to point at a local build (`python -m http.server` on a built site) so the tests can
  run offline.
- A pytest file `product/nz_election/tests/test_night_deployed.py` that runs the script's check
  functions against a local built site with fixtures (offline, skipped cleanly when Chromium is
  absent, like night_browser.py). Unit-test the record writer and golden comparison without a browser.
- No secrets, no new dependencies beyond playwright already used. Existing tests untouched except
  where a registered set must grow to include the new file.
- artifacts/ stays untracked; do not commit screenshots or records.

## Definition of done

- `uv run --with pytest pytest -q product/nz_election/tests/test_night_deployed.py` passes.
- `uv run --with pytest pytest -q` passes overall; `bin/lint` prints ok.
- Run `uv run --with playwright python product/nz_election/tests/night_deployed.py --probe` against
  the live origin once if network allows; if the sandbox blocks network, say so in last.md and run
  it with `--base-url` against a local build instead. Same for `--rehearse --speed 60` (about 10 s of
  replay; give the elapsed times) and `--faults`. Paste each final line.
- Commit on the branch; last.md lists files, commands and their last lines, and anything that would
  need the supervisor to rerun on the host.
