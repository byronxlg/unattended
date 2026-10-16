Fresh-context review of branch change/remove-fleet-audit against main, for PR #8 (Remove the
rejected Fleet Audit product from main), HEAD d23db78. Context: Byron rejected the Fleet Audit
product in GitHub issue #7; the code leaves main, history stays. The brief is in
state/jobs/remove-fleet-audit/prompt.md (read it: it states the invariant and what must not
be touched). Review `git diff main...HEAD -- . ':!product/**'` closely (it is small) and
`git diff --stat main...HEAD` for the deletion's extent.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with the brief). Severity Important or Nit, at most five nits, do not
report what bin/lint reports. Do not approve; the supervisor decides.

Check in particular:
1. Nothing outside product/fleet_audit and runbook/fleet/fleet.md was deleted that something
   still needs: any remaining reference in bin/, tests/, .github/, runbook/, AGENTS.md,
   CLAUDE.md to a path or command that no longer exists.
2. .github/workflows/ci.yml still runs the root tests and bin/lint; the test guard is correct
   with no product/tests present; no check was weakened or skipped to pass.
3. tests/fixtures/metrics/real: the engineer relabelled the product slug to retired-product
   in changes.yaml and mistakes.jsonl and amended the README. Confirm every metric input
   (timestamps, outcome, prs, plan_match, origin, occurrences count) is unchanged and the
   expectations in tests/test_metrics_indicators.py::test_frozen_state_totals still follow.
4. intent/, posts/, state/, docs/, evals/ and the Known agent mistakes section of CLAUDE.md
   are untouched.

Running checks: try `uv run --with pytest pytest -q` from the worktree root; if the sandbox
cannot run it, say so and review by reading. The supervisor's run at d23db78 stands: 84
passed, bin/lint ok, the invariant rg prints nothing.

Output: a list of findings, each with severity, file:line, what is wrong, why it matters,
and a one-line suggested fix. End with one line: the count of Important findings.
