# Answer first, then the brief again

Your previous run of this brief ended after you asked: "May I use the suggested route: infer
successful deploys from successful runs and fetch job details only for failed runs?" Nobody
can answer a question mid-run here: Codex runs non-interactively and the run died. Answer:
yes. Use the suggested route. The bound you state in `test_github_bounded_calls` is a
constant, plus a term in the number of linked PRs, plus a term in the number of Pages runs
whose conclusion is in `FAILURES`. Never a term in the number of Pages runs. Say that bound
in the test's docstring. From now on, when a brief offers a route and the strict wording
conflicts, take the route and record the choice under "Implementation departures"; do not ask.

# Fix: lab metrics, supervisor review and first fresh review findings

Same worktree `.worktrees/lab-metrics`, branch `change/lab-metrics`, HEAD 403e1a4, PR #6.
Commit in the worktree; never push. Fixtures under `tests/fixtures/metrics/real/` unchanged.
Under `tests/` you may change exactly what each item below names, plus the new tests it asks
for; nothing else. Record each departure from `intent/lab-metrics/plan.md` under its
"Implementation departures" heading in the same commit.

## Important 1: the number of gh subprocesses grows with the number of Pages runs

`read_github` schedules `actions/runs/{id}/jobs` for every Pages run, two at a time, inside
the 45 s budget. Measured at 403e1a4: 48 Pages runs plus 5 linked PRs is 67 detail calls and
`bin/metrics --json -` takes 26.6 s wall time. The lab adds roughly 30 Pages runs a day
(every push to main), so by about day 3 `batch` marks the remaining `jobs:<id>` sources
unavailable, and because `deploy_deps` carries every one of them, `deployment_frequency`,
`deployment_lead_time` and `restore_time` become unavailable for the rest of the lab.

Invariant: the count of gh subprocesses per run of `bin/metrics` is bounded by a constant
plus a term in the number of linked PRs, never a term in the number of Pages runs. The
spec rule stands: a deployment is a successful `deploy` job; successful builds without a
successful deploy job are not deployments; cancelled runs are neither deployments nor
incidents. How you get there is yours. One route: `pages.yml` has two jobs, `build` and
`deploy` with `needs: build` and no `continue-on-error`, so a run whose `conclusion` is
`success` had a successful `deploy` job, and the run's `updated_at` is a proxy for that
job's `completed_at` that must be named in the indicator notes; per-run job detail is
then needed only for runs whose conclusion is in `FAILURES`, to tell a failed deploy job
from a skipped one, which is bounded by the failure count. Whatever route you choose,
`deploy_deps` must list only sources that were actually fetched.

Where it is enforced: add `test_github_bounded_calls` to `tests/test_metrics_sources.py`.
It stubs the client's subprocess boundary with a counter, feeds 500 synthetic Pages runs
(mixed `success`, `failure`, `cancelled`), two linked PRs, and asserts the call count is
under a fixed bound you state in the test, and that the three DORA indicators come out
`available: true` from `compute`. Add or adjust an indicator test so the three DORA rows
still give the plan's expected results on the synthetic fixtures (daily zeros, exact merge
SHA, red-red-green episode).

## Important 2: the integration test asserts live state totals

`tests/test_metrics_integration.py::test_real_state_under_60_seconds` reads the repository's
mutable `state/` and asserts `rework_cycles == 17`, `repeated_mistakes == 1` and
`plan_to_final_merge` unavailable. The supervisor records `attempts: 1` for `lab-metrics`
in `state/changes.yaml` at merge, which changes the mean and fails CI on main with no
metrics regression. Invariant (plan, Tests section): tests never depend on real state
values. Keep the real-state test to what is invariant under ledger growth: wall time under
60 s, 56 indicators, every row has the full key set, and no exception. Move the exact
numbers to the frozen fixtures: the real fixture set already carries Fleet Audit with
attempts 11 and five linked PRs per `tests/fixtures/metrics/README.md`, and the synthetic
set has its documented expectations. That one test function is the only change allowed in
that file.

## Important 3: chronological comparisons on ISO strings

`compute.py` compares normalized timestamps as strings (`post_fixes`, `final`, `caught`,
`lead`, the gate warning, the snapshot sort). `timestamp()` emits microseconds only when
they are nonzero, and `.` sorts before `Z`, so a fix starting at `06:00:00.5Z` after a merge
at `06:00:00Z` is excluded from the change failure rate. The fresh review reproduced it.
Invariant: ordering two normalized timestamps must not depend on their formatting. Compare
parsed datetimes, or make `timestamp()` emit one fixed precision for every input and say so
in a comment; your choice, applied to every comparison and sort, not one instance. Add
`test_fractional_second_fix_counts_after_merge` to `tests/test_metrics_indicators.py`.

## Nit, optional

`deployment_frequency` builds each daily sample's stamp with a literal `+13:00`. It buckets
correctly under both NZ offsets, but the plan says never a fixed offset. Build it from
`ZoneInfo("Pacific/Auckland")` if you touch that code.

## Definition of done

From the worktree root: `uv run --with pytest pytest -q` with zero failures and at least
84 tests; `bin/lint` printing `lint ok`; `time bin/metrics --json - >/dev/null` showing real
time under 15 s with today's 48 Pages runs; `bin/metrics --json - | python3 -c 'import json,sys; d=json.load(sys.stdin); print([ (i["name"], i["available"], i["n"]) for i in d["indicators"] if i["stage"]=="CI/CD"])'`
showing the three DORA rows available with n above 0; `git diff --stat 403e1a4` touching
only `lab_metrics/`, `tests/` and `intent/lab-metrics/plan.md`. Final message under 15
lines: commit hash, the outputs, anything you could not do.
