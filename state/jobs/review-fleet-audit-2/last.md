Malformed plists can leak environment secrets, and captures of invalid registries can fail their own replay validation. Observer acceptance passed; full tests were unavailable because uv cache access was blocked and the existing environment lacked pytest.

Full review comments:

- [P1] Discard unredactable plist bytes before archive export - /Users/byron/repos/unattended/.worktrees/fleet-audit-2/product/fleet_audit/fleet_audit/capture.py:44-46
  If a plist contains environment secrets but is malformed, such as XML missing its closing tag, this exception handler retains the original bytes. `emit_archive` then exports those secrets unchanged. Verified with a malformed fixture containing an EnvironmentVariables token. Record an invalid-plist observation without raw bytes when safe redaction is impossible.

- [P2] Skip plist-entry requirements when registry validation fails - /Users/byron/repos/unattended/.worktrees/fleet-audit-2/product/fleet_audit/fleet_audit/snapshot.py:219-222
  For duplicate projects or identities, registry loading retains jobs alongside validation errors, so capture correctly skips the plist join and records no plists. This unconditional check then rejects the capture's own snapshot with `missing plist entry`, preventing replay from reporting the actual registry errors. Reproduced with both duplicate-project and duplicate-identity fixtures. Require plist entries only when registry validation permits the join.