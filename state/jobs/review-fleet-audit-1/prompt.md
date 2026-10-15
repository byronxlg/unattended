Fresh-context review of branch change/fleet-audit-1 against main, for PR #1 (Fleet Audit
increment 1: registry and plist join). Follow REVIEW.md in the repository root: three passes
in order (bugs and logic errors; security; compliance with intent/fleet-audit/spec.md and
plan.md "Increment 1" and "Increment 1 CI step"). Severity Important or Nit, at most five
nits, do not report what bin/lint reports. Do not approve; the supervisor decides.

Focus for this diff:
- registry.py restricted YAML loader: any accepted input that the spec's schema table rejects,
  or rejected input that the spec accepts (aliases, tags, nulls, duplicate keys, implicit
  coercion, quoted `reviewed`).
- files.py bounded reader and discovery: hangs, symlink traversal, the 1 MiB and 1,000-file
  bounds, exceptions that escape as tracebacks.
- plists.py: any plist content that reaches a record as an environment value; exceptions from
  plistlib not caught.
- reports.py and cli.py: exit codes per spec section "Exit precedence" for declared (0 valid
  nonempty, 3 otherwise), stable escaped text lines, JSON shape.
- tests/conftest.py guards and acceptance.py offline guard: can live access slip past them.
- Fixtures: anything that is a real captured value but labelled synthetic or vice versa;
  any environment value.
- Package contains no subprocess import and no launchctl code (increment 1 scope).

Output: a list of findings, each with severity, file:line, what is wrong, how to reproduce or
why it matters, and a one-line suggested fix. End with one line: the count of Important findings.
