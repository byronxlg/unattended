Fresh-context review of branch change/fleet-audit-5 against main, for PR #5 (Fleet Audit
increment 5: scan, complete reports and lab adoption), third round after fix commit e2c946e.
Follow REVIEW.md in the repository root: three passes in order (bugs and logic errors;
security; compliance with intent/fleet-audit/spec.md "CLI and report contract", the scan
paragraphs, supervisor decisions 1, 2, 6, 9 and 11, and plan.md "Increment 5: scan, reports
and lab adoption"). Severity Important or Nit, at most five nits, do not report what bin/lint
reports. Do not approve; the supervisor decides.

Running checks: uv's cache is not writable in this sandbox, so do not use `uv run`. From
product/fleet_audit, run `.venv/bin/python -B -m fleet_audit.acceptance fleet --offline` (and
the registry, observer, verdicts and drift stages the same way). If pytest is not importable
from that venv, say so and review by reading; do not install.

Previous rounds, both fixed on the build thread:
- d00b16b: scan.py scan_fleet carries plist field_errors into uncertainties; receipts.py
  timestamp catches OverflowError with ValueError.
- e2c946e (diff d00b16b..e2c946e, the focus of this round): scan.py gains PLIST_KEYS and
  unsupported_plist_uncertainties, which walks PlistData and its Schedule for Unsupported
  values and appends `plist: {Key}: {reason}` to the job's uncertainties, deduplicated with
  dict.fromkeys; files.py stat_output catches (OSError, ValueError, OverflowError) and reports a
  conversion failure as a stat error with exists True. Two new tests in tests/test_reports.py.

Focus for this round:
- Is e2c946e complete and correct: does unsupported_plist_uncertainties cover every field that
  can hold an Unsupported value today (plists.py produces one only for KeepAlive mappings; say
  if any other producer exists); is the dedupe order stable; does the field walk ever recurse
  into something other than Schedule; is exists True right for a conversion failure (the stat
  succeeded, the timestamp did not) and does any consumer of OutputData treat exists True with
  mtime None as healthy anywhere (verdicts.py rules 10 to 12, output.py age, snapshot.py
  replay and capture).
- Does anything in audit mode change because of e2c946e (scan_fleet is scan only; stat_output
  is shared, so an audit job whose output file has an out-of-range mtime now gets a stat error
  instead of a traceback: confirm that lands on rule 10 as unavailable evidence timestamp, not
  on healthy_idle).
- The two new tests assert what their names say; no existing test or fixture changed in
  e2c946e; tests/conftest.py unchanged.
- One whole-branch spot check: any remaining place in scan or audit where a plist, service or
  receipt value the tool classified as Unknown or Unsupported is retained in evidence but
  absent from both the job's uncertainties and its comparisons, so the summary count and exit
  code cannot see it.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
