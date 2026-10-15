# Fix: Fleet Audit increment 2, supervisor review findings

Same worktree `.worktrees/fleet-audit-2`, branch `change/fleet-audit-2`, HEAD 0608dd0. Commit
in the worktree; never push. Tests stay as they are unless a finding names one.

## Important: obfuscated string in acceptance.py

`fleet_audit/acceptance.py` line 27 now reads `event.startswith("sub" "process.")`. The literal
was split so that the brief's check `rg -l subprocess product/fleet_audit/fleet_audit` would
list only `collect.py`. That hides the word from a reviewer's grep without changing behaviour,
which is the wrong way to satisfy a check. Restore the literal `"subprocess."`. The supervisor
has changed the verification to an import grep: `rg -l '^(import|from) subprocess'
product/fleet_audit/fleet_audit` must list exactly `collect.py`. When a verification command in
a brief cannot be satisfied honestly, say so in the final message instead of working around it.

## Nit: capture re-serialises every plist

`capture.py` `RecordingFiles.read_regular` round-trips every parsed plist through
`plistlib.dumps`, so binary plists become XML and byte identity is lost even when there is no
`EnvironmentVariables` key, and a malformed plist is replaced by `data=None` plus an
`invalid_plist` error rather than kept as the malformed bytes the plan says to retain. Change it
to: keep the original bytes when the plist parses and has no `EnvironmentVariables` key; redact
and re-dump only when the key is present; when parsing fails, keep the original bytes unchanged
(replay's `parse_plist` reports the malformed structure itself). Add one assertion to
`test_capture_roundtrip_and_environment_redaction` that a plist without environment keeps its
bytes identical.

## Nit: undocumented shim

`snapshot.py` `load_snapshot` accepts a `launchctl list` exit-1 record under the
`print <domain>` command key (`legacy`). Add a one-line comment saying why: the real blank
inventory record from spike commit 18c8e8c is a `list` call and the plan requires replaying it.

## Definition of done

From `product/fleet_audit/`: `uv run python -m fleet_audit.acceptance registry --offline`
(`OK registry`), `uv run python -m fleet_audit.acceptance observer --offline` (`OK observer`),
`uv run --with pytest pytest -q` (zero failures). From the worktree root: `bin/lint` exit 0,
`rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit` prints only `collect.py`.
Final message under 20 lines: commit hash, the outputs, anything you could not do.
