Fresh-context review of branch change/fleet-audit-4 against main, for PR #4 (Fleet Audit
increment 4: three-way drift). Follow REVIEW.md in the repository root: three passes in order
(bugs and logic errors; security; compliance with intent/fleet-audit/spec.md sections "Drift
comparison", "Verdict decision order" rule 9, "CLI and report contract", supervisor decisions
7 and 8, and plan.md "Increment 4: three-way drift", "Shared records and boundaries" (Drift
boundary), "Snapshot and fixture format"). Severity Important or Nit, at most five nits, do
not report what bin/lint reports. Do not approve; the supervisor decides.

Running checks: uv's cache is not writable in this sandbox, so do not use `uv run`. From
product/fleet_audit, run `.venv/bin/python -B -m fleet_audit.acceptance drift --offline` (and
the registry, observer and verdicts stages the same way) and `.venv/bin/python -B -m pytest -q`.
If pytest is not importable from that venv, say so and review by reading; do not install.

Focus for this diff (b786941..399812d):
- drift.py compare_job: any finding emitted when either side is Unknown, Unsupported or
  Absent; any comparison emitted for an Absent expectation; loaded pairs anything other than
  not_applicable when loaded is Known(False); loaded evidence used when loaded is Unknown or
  structural_valid is false; the disk program ever taken from anywhere but Program then
  ProgramArguments[0]; argv ever invented from Program, shell-split, expanded, reordered or
  trimmed (empty strings and spaces must survive); a path compared after realpath or
  expansion; the reason string ever departing from
  `{field}: {left_source}={left_value} differs from {right_source}={right_value}`; a kind
  other than wrong_program, wrong_arguments, wrong_working_directory, wrong_schedule; a
  requested schedule component skipped or an unrequested one compared; evidence refs that do
  not name the observations actually used.
- drift.py normalize_calendar: alternative order, map key order and duplicate alternatives
  changing the result; Sunday 7 not mapped to 0 in Weekday only (Day 7 must stay 7); an
  omitted key ever equal to a value; duplicate keys within one alternative accepted; any
  exception (TypeError on sorting mixed types, ValueError) escaping on malformed input.
- launchctl_parse.py changes: a loaded KeepAlive or RunAtLoad ever Known without the frozen
  supported `keepalive`/`runatload` property token; an event trigger that is not a calendar
  interval ever producing a Known calendar or a Known interval; the real records under
  fixtures/observer (tick runatload, skhd keepalive, PDW calendar, talagent two calendars)
  still parsing exactly as before this diff; any regression in increment 2 observer tests.
- Decision 7: drift never reads rule 8's disk fallback for loaded policy; disk omitted
  KeepAlive/RunAtLoad normalize to false (plists.py, unchanged) and compare against a loaded
  Unknown as unknown, never as different.
- reports.py and verdicts.py: exit 1 on any drift finding regardless of verdict except when
  invalid input (3) takes precedence; a running job keeps verdict running with its drift
  retained; rule 9 blocks healthy_idle on any unknown required comparison; JSON output
  serialises Comparison left/right values (Known, Unknown, Unsupported, Absent) without
  raising; text output lists every finding.
- acceptance.py prove_drift: runs under the offline guard with the live-clock traps; refuses
  reviewed false; asserts findings equal exactly the set of different comparisons.
- Fixtures: every snapshot under fixtures/drift is labelled synthetic with its timestamp
  limitation; expected.json values match the spec (not copied from evaluator output);
  manifests reference members by byte count and SHA-256; no environment value anywhere.
- Tests: tests/conftest.py unchanged; increment 1 to 3 tests and fixtures unchanged; every
  test the plan's increment 4 names is present and asserts what its name says; no test
  spawns a process.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
