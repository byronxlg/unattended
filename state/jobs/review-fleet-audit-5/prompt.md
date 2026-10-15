Fresh-context review of branch change/fleet-audit-5 against main, for PR #5 (Fleet Audit
increment 5: scan, complete reports and lab adoption). Follow REVIEW.md in the repository root:
three passes in order (bugs and logic errors; security; compliance with
intent/fleet-audit/spec.md sections "CLI and report contract", the scan paragraphs, rule 5 of
"Verdict decision order", supervisor decisions 1, 2, 6, 9, 11 and 13, and plan.md "Increment 5:
scan, reports and lab adoption", "Shared records and boundaries", "Snapshot and fixture
format"). Severity Important or Nit, at most five nits, do not report what bin/lint reports.
Do not approve; the supervisor decides.

Running checks: uv's cache is not writable in this sandbox, so do not use `uv run`. From
product/fleet_audit, run `.venv/bin/python -B -m fleet_audit.acceptance fleet --offline` (and
the registry, observer, verdicts and drift stages the same way) and
`.venv/bin/python -B -m fleet_audit.cli scan --fixture fixtures/fleet/real-twelve` (note the
exit code). If pytest is not importable from that venv, say so and review by reading; do not
install.

Focus for this diff (4e9dbbf..e6e4600):
- scan.py scan_plists: a valid label beginning com.apple. ever retained; an unreadable or
  no-label plist excluded by anything other than the exact filename prefix com.apple.
  (com.appleish must survive); a label ever derived from a filename; a no-label row ever
  dropped or ever given a service lookup; discovery error handling (data None) and the
  coverage it produces.
- scan.py scan_fleet: a declared stdout/stderr path stat'd more than once or ever read
  (read_tail, read_regular on it); any freshness verdict (late, healthy_idle) reachable in scan
  mode; the no-label override applied after evaluate (is anything from evaluate lost that
  should be kept, e.g. uncertainties); the output:N keys and the not_requested output
  observation both present in JSON.
- verdicts.py evaluate scan mode: rule 5 reason exactly `plist on disk, service absent; not
  declared`; rule 10 reason `no freshness contract declared`; loaded_disabled emitted directly
  and exiting 1 (decision 9); scan disabled exiting 2 with expected_enabled=unknown in the
  reason; any rule that dereferences job.registry or job.project without a None guard.
- collect.py: the None-label branch (service Observation not_applicable, loaded Unknown); the
  rc=unknown rendering; any path where a None label reaches launchctl argv.
- reports.py: the text line format `{project_or_scan}/{id_or_plist} {domain}/{label_or_no_label}
  {verdict}: {reason}` and escaping of newlines, tabs, quotes, backslashes and control
  characters; stable job order for scan (by plist path); exit_code precedence 3, 1, 2, 0 across
  jobs and issues; empty or incomplete coverage never 0; declared text on errors now printed to
  stderr by cli.py (is anything lost versus the previous per-error stderr lines).
- snapshot.py: scan replay refusing an audit snapshot and vice versa; validate_entries in scan
  mode touching every command and stat the replay will need so a missing member fails before
  any report; the relaxed output_observation check (exists true with size null) accepting
  anything it should not; SnapshotFiles.discover_plists reusing the discovery index.
- capture.py scan mode: every plist read goes through the redaction path; stdout/stderr stats
  deduplicated; no runbook members; expected.json is {"reviewed": false}; no environment value
  can reach the archive through any member.
- receipts.py: ts now normalised to UTC Z; any increment 3 verdict or age computation changed
  by that.
- files.py discover_plists: symlinked directory refused; non-recursive; the 1000 bound
  enforced while enumerating; permission errors returned as discovery errors, never raised.
- Fixtures: all ten plan fixtures plus real-twelve under fixtures/fleet; each labelled with
  kind, mode, source and timestamp limitation; expected.json values match the spec decisions
  (not copied from evaluator output); no environment value anywhere (the redaction fixture's
  placeholder is empty); real-twelve's composition honestly described in fixtures/README.md.
- Tests: tests/conftest.py unchanged; increment 1 to 4 tests and fixtures unchanged; every
  test the plan's increment 5 names is present and asserts what its name says; no test spawns
  a process; the fleet acceptance refuses reviewed false.
- CI: .github/workflows/ci.yml gained exactly one line. runbook/ untouched.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
