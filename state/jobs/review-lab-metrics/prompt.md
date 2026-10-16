Fresh-context review of branch change/lab-metrics against main, for PR #6 (Lab metrics:
bin/metrics, lab_metrics/ package, Pages generation), first round, HEAD 403e1a4.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with docs/metrics.md, which is the spec, and intent/lab-metrics/plan.md
including its seven supervisor decisions at the end). Severity Important or Nit, at most
five nits, do not report what bin/lint reports. Do not approve; the supervisor decides.

Pattern named up front (plan decision 7): every value read from a ledger, YAML, git or the
API is untrusted. Timestamp parsing, numeric coercion and timezone conversion must degrade
to a counted diagnostic, never raise; and every shape compute emits must be accepted by
render_document. Look for the pattern, not one instance: any key access, comparison,
arithmetic or sort in lab_metrics/compute.py that can raise or silently misorder on a value
sources.py lets through (None, bool, str where int expected, fractional-second timestamps,
nested non-dict), and any emitted structure render.py would reject or mangle.

Running checks: uv's cache may not be writable in this sandbox. Try
`uv run --with pytest pytest -q` from the worktree root; if it cannot run, say so and review
by reading. The supervisor's run at 403e1a4 stands: 81 passed, bin/metrics printed
`metrics: 56 indicators, 12 unavailable, 0 skipped`, two runs byte-identical, bin/lint ok.
Do not run bin/metrics against live GitHub.

Already found by the supervisor, do not re-report: read_github schedules one gh subprocess
per Pages run so the 45 s budget is exceeded as runs accumulate (a fix job follows);
timestamps compared as strings; the literal +13:00 in deployment_frequency samples;
supervisor_*_runs naming.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
