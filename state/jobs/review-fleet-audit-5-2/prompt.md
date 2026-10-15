Fresh-context review of branch change/fleet-audit-5 against main, for PR #5 (Fleet Audit
increment 5: scan, complete reports and lab adoption), second round after fix commit d00b16b.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with intent/fleet-audit/spec.md "CLI and report contract", the scan
paragraphs, supervisor decisions 1, 2, 6, 9 and 11, and plan.md "Increment 5: scan, reports
and lab adoption"). Severity Important or Nit, at most five nits, do not report what bin/lint
reports. Do not approve; the supervisor decides.

Running checks: uv's cache is not writable in this sandbox, so do not use `uv run`. From
product/fleet_audit, run `.venv/bin/python -B -m fleet_audit.acceptance fleet --offline` (and
the registry, observer, verdicts and drift stages the same way). If pytest is not importable
from that venv, say so and review by reading; do not install.

The previous round (fixture: state/jobs/review-fleet-audit-5/last.md is not visible to you;
summary here) found two Important items, fixed in d00b16b (diff e6e4600..d00b16b):
1. scan.py scan_fleet dropped plist field errors from uncertainties, so a running service with
   an invalid StandardOutPath exited 0. Fix appends `plist: {message}` per field error to the
   job's uncertainties before evaluate.
2. receipts.py timestamp raised an uncaught OverflowError from astimezone for
   0001-01-01T00:00:00+01:00. Fix catches OverflowError with ValueError.

Focus for this round:
- Are the two fixes complete: any other place in scan mode where a plist's field_errors, or
  an Unknown/Unsupported plist field, is silently dropped from uncertainties or the summary
  count; any other datetime conversion in receipts.py, output.py, files.py or collect.py that
  can raise (OverflowError, OSError, ValueError) on hostile input and is not caught; does the
  uncertainty count in the summary and the text `uncertainty:` lines now include the plist
  field errors.
- Does the first fix change any audit behaviour (audit exits 3 on field errors before this
  code runs; confirm nothing in audit mode now double-reports).
- The two new tests in tests/test_reports.py: assert what their names say; no existing test
  or fixture changed in d00b16b; tests/conftest.py unchanged.
- Whole-branch spot checks you can do quickly: scan label filter (valid com.apple. labels
  excluded; unreadable or no-label plists excluded only by exact com.apple. filename prefix;
  no filename ever becomes a label; no service lookup for a no-label row); stdout/stderr paths
  stat'd once per unique path and never read; no late or healthy_idle reachable in scan mode;
  exit precedence 3, 1, 2, 0; environment values absent from text, JSON and snapshots.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
