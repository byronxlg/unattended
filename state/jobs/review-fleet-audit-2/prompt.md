Fresh-context review of branch change/fleet-audit-2 against main, for PR #2 (Fleet Audit
increment 2: observer and replay). Follow REVIEW.md in the repository root: three passes in
order (bugs and logic errors; security; compliance with intent/fleet-audit/spec.md sections
"Evidence record and collection" and "Offline replay and verification", decisions 7, 9, 10, 11
and 12, and plan.md "Increment 2: observer and replay", "Shared records and boundaries",
"Validation and observation policy", "Snapshot and fixture format"). Severity Important or Nit,
at most five nits, do not report what bin/lint reports. Do not approve; the supervisor decides.

Focus for this diff:
- collect.py run_bounded: can a child outlive the call (timeout, output limit, spawn failure,
  exception between Popen and the finally); can the combined limit be exceeded; is return_code
  null exactly when the spec says; any path where argv is not the fixed launchctl form.
- launchctl_parse.py: input that establishes loaded=true without a structurally valid,
  identity-matching response; a 113 response that is accepted with the wrong label or uid;
  nested coalition state reaching root state; duplicate fields not rejected; tree() on
  adversarial text (deep nesting, unmatched delimiters) raising anything other than ValueError.
- overrides.py: a failed or partial map ever becoming a known empty map; precedence against
  decision 10 and the spec's effective disabled rule.
- snapshot.py load_snapshot and replay: any read of a path outside the snapshot directory, any
  symlink follow, any live clock or subprocess use on the replay path; member integrity
  checks that can be bypassed; the legacy launchctl list shim accepting more than the one
  blank exit-1 record.
- capture.py: any filesystem write; any environment value surviving into plist bytes or
  command streams (including inherited and default environment blocks).
- verdicts.py: rule 1 matching when it should not (an absent service with exact 113) or not
  matching when it should (structural failure, failed inventory, failed override map).
- Fixtures: a real record without a source and capture time, a synthetic record labelled real,
  any environment value, the five disabled Apple labels present.
- Tests: tests/conftest.py unchanged; the increment 1 tests changed only to allow collect.py
  in the AST check; the plan's increment 2 tests present and asserting what their names say.

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
