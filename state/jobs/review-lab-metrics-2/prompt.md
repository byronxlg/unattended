Fresh-context review of branch change/lab-metrics against main, for PR #6 (Lab metrics:
bin/metrics, lab_metrics/ package, Pages generation), second round, HEAD bfe2380. The first
round (403e1a4) found two Important items and the supervisor one; all three were fixed in
bfe2380. Review the whole branch, with most attention on the fix commit:
`git diff 403e1a4..bfe2380`.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with docs/metrics.md, which is the spec, and intent/lab-metrics/plan.md
including its seven supervisor decisions and the "Implementation departures" at the end).
Severity Important or Nit, at most five nits, do not report what bin/lint reports. Do not
approve; the supervisor decides.

What the fix changed and what to check about it:
1. read_github fetches actions/runs/{id}/jobs only for Pages runs whose conclusion is in
   FAILURES; compute treats a run with conclusion success as a successful deploy job using
   updated_at as the completion proxy, uses job evidence when a jobs:<id> source exists,
   skips cancelled runs, and marks the three deploy indicators unavailable when a failed
   run has no job source or a successful run has an invalid updated_at. Check: every path
   through that loop for a run shape sources.py lets through (conclusion None, missing
   updated_at, id not an int, head_sha missing); deploy_deps lists only sources actually
   fetched; a jobs:<id> source that batch marked unavailable still makes the indicator
   unavailable; tests/test_metrics_sources.py::test_github_bounded_calls states and proves
   the bound 4 + 3 * linked PRs + failed Pages runs.
2. Chronological comparisons and sorts in compute.py go through dt() (parsed datetime)
   instead of string order. Check the pattern across the whole file, not one instance: any
   remaining string comparison or sort on a timestamp field, and any dt() call that can
   receive None after the timestamp() guard (dt(None) returns None, and None < datetime
   raises TypeError).
3. tests/test_metrics_integration.py::test_real_state_under_60_seconds now asserts only
   wall time, row count and key set; exact totals moved to test_frozen_state_totals on the
   frozen fixtures with seven synthetic fix jobs. Check the integration test cannot fail on
   normal ledger growth and that the frozen test's expectations follow from the fixture.

Pattern named up front (plan decision 7): every value read from a ledger, YAML, git or the
API is untrusted; parsing, coercion and timezone conversion degrade to a counted diagnostic,
never raise; every shape compute emits is accepted by render_document.

Running checks: uv's cache may not be writable in this sandbox. Try
`uv run --with pytest pytest -q` from the worktree root; if it cannot run, say so and review
by reading. The supervisor's run at bfe2380 stands: 84 passed, bin/lint ok, bin/metrics
--json - in 8.2 s real, the three deploy indicators available with n 2, 3, 1. Do not run
bin/metrics against live GitHub.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
