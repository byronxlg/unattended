# Build brief: nz-election increment 4 (coalition explorer)

You are the engineer in the unattended lab (read AGENTS.md, then product/nz_election/AGENTS.md).
You are in the worktree `.worktrees/nz-election-4` on branch `change/nz-election-4`, based on
main at 307febd: M1 is merged and live (PRs #9, #10, #11; 240 tests; six routes; hourly workflow
publishing to the `data` branch; https://byronxlg.com/unattended/nz-election/ serves 43 polls).
Commit there; never push. No network in your sandbox; builds and tests are offline.

## Goal

Increment 4 of intent/nz-election/plan-m2.md "Build order", the first M2 increment: the
coalition explorer (spec requirement 4) on the polls page. Read, in order:
intent/nz-election/plan-m2.md (sections "Coalition explorer", "Design and accessibility",
"Verification and test inventory", "Build order", and "Supervisor decisions", which override the
body), intent/nz-election/spec.md requirement 4 and its Design section, then the code:
pipeline/build.py (route handling and the polls page rendering), pipeline/verify.py (the check
registry and `PASS all`), pipeline/allocator.py and web/allocator.mjs (`allocate`,
`entitlement`), pipeline/export.py (envelope and validators), web/templates/polls.html and
base.html, web/styles.css (tokens), tests/test_build.py, tests/screenshots.py,
tests/allocator_runner.mjs (the existing Node parity pattern), config/routes.json.

No new captures. Inputs are the published `averages.json` and `seats.json` the polls page already
renders. Deliverables, as the plan names them: `pipeline/coalitions.py`, `web/coalitions.mjs`,
a small Node runner under tests/, `tests/test_coalitions.py`, `tests/coalitions_browser.py`
(host-run, Playwright), the `coalitions` entry in the verify.py registry, template and CSS
changes on the polls page.

## Invariants (name where each is enforced; choose the shapes yourself, then check your diff against the enforcer)

1. Static first. The polls page without JS shows the calculated seats, the majority line and
   provenance exactly as today; the explorer controls are hidden or inert with a one-line note.
   Enforced by `verify.py` and `tests/coalitions_browser.py` (JS-disabled context) and by the
   M1 static checks you are replacing (next item).
2. The script prohibition becomes a script allowlist. Today `verify.py:41`, `test_build.py:36`
   and the build reject any `<script`. Replace that with: only `<script type="module">` tags
   whose `src` is a named, same-origin, prefix-relative local file from an explicit allowlist
   (`coalitions.mjs`, `allocator.mjs` as its import); no inline script bodies; the injection
   tests (test_build.py:65 onward) keep passing unchanged. The plan calls this a deliberate
   replacement of an M1-only assertion; say so in your report and keep every other existing test
   untouched.
3. Exact arithmetic. Seat maths goes through the existing allocator (`entitlement()` when list
   capacity is unchecked, which is the state this increment ships; `allocate()` only with real
   candidate IDs, which do not exist yet). BigInt in JS, int/Fraction in Python. Never a float.
   Enforced by `test_scenario_python_js_parity` (same scenarios through both, byte-equal JSON).
4. Majority is `floor(occupied_house / 2) + 1` and stays conditional while capacity is unchecked:
   `occupied_house`, `vacancies`, definitive `majority` null as M1 publishes them; the explorer
   shows "Seats needed for a majority" against the assumed House and says it is assumed.
   Enforced by `test_unknown_capacity_stays_conditional`.
5. No preselected coalition. Default state is empty; Reset returns to it. Others is never
   selectable. Electorate wins are whole non-negative integers totalling at most 71, the 2026
   scenario starts from `71 - sum(2023 wins)` unassigned with the boundary-change label.
   Enforced by `test_no_preselected_coalition` and the browser test.
6. Hash state is untrusted input. `#coalition=<percent-encoded JSON>` with a version, selected
   party IDs, counts, mode, input fingerprint. One validator in Python and one in JS with the
   same `INVALID_COALITION_STATE` outcomes for: empty, null, wrong type, fractional, huge
   integers (bound the string length before conversion), Unicode, `__proto__` and prototype-like
   keys, duplicates, unknown IDs, oversize hash. Everything rendered goes through textContent.
   Enforced by `test_invalid_state_error_parity`. A fingerprint mismatch warns, it does not
   silently apply.
7. Incomplete inputs disable the explorer, never approximate: mismatched average IDs, a missing
   party in the window, a failed module or data request leaves the static content intact.
   Enforced by `test_incomplete_average_disables_explorer`.
8. Design: reuse the seat strip (counts inside segments, lanes for small segments, the majority
   marker), 44 px controls, visible 3 px `#005EA8` focus, 4.5:1 text contrast, reduced motion
   respected, a polite live region announcing the selected total and the majority requirement,
   voter copy ("Choose parties", "Electorate seats assumed", "Seats needed for a majority"), no
   meaning by colour alone, no page-wide overflow at 390 px. Enforced by the browser test and the
   screenshots the supervisor inspects.
9. Screenshot contract unchanged: six routes, 12 baseline images, `PASS screenshots: 6 routes,
   12 baseline images`. Add the coalition edit and coalition vacancy states at both sizes to the
   existing state images and say the new total in the report.

## Definition of done (print the exact lines; the host-run ones you cannot run, say so)

```
uv run --with pytest pytest -q                       # all pass; report the count (target about 252)
uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election   # PASS build: 6 routes
uv run product/nz_election/pipeline/verify.py coalitions                                        # PASS coalitions
uv run product/nz_election/pipeline/verify.py all                                               # ends PASS all
node product/nz_election/tests/<your runner>.mjs ...                                            # parity, as test_coalitions.py invokes it
bin/lint                                              # lint ok (N text files), after staging new files
```
Host-run by the supervisor after you land (Playwright and Chromium are on the host, not here):
```
uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site site    # PASS coalition browser
uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots   # PASS screenshots: 6 routes, 12 baseline images
```

## Constraints

- One commit per coherent step is fine; do not edit `state/`, `posts/`, `prompts/`, `intent/`,
  fixtures, or existing tests other than the two script-prohibition assertions named above.
- No runtime dependencies, no bundler, no fonts, no inline scripts, no float anywhere in seat maths.
- Departures from the plan go in a "Departures" list in your final report with the reason.
- Final report (your last message): what you built, the verification output quoted, departures,
  the new test count, the state image total, anything the supervisor must run on the host.
