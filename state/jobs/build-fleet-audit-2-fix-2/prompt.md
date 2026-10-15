# Fix 2: Fleet Audit increment 2, fresh-review findings

Same worktree `.worktrees/fleet-audit-2`, branch `change/fleet-audit-2`, HEAD 90b239e. Commit
in the worktree; never push. Existing tests stay as they are; add assertions only as named.

## Important 1: malformed plist bytes can leak environment values (capture.py:44-46)

The previous fix made `RecordingFiles.read_regular` keep the original bytes when `plistlib`
cannot parse a plist. A malformed plist (for example XML missing its closing tag) that contains
`EnvironmentVariables` values would then reach `emit_archive` unredacted. The supervisor's
earlier instruction to keep malformed bytes was wrong; decision 11 (no environment values,
anywhere) wins. Required behaviour: a plist that parses and has no `EnvironmentVariables`
keeps its original bytes (byte identity test stays); a plist that parses with the key is
redacted and re-dumped; a plist that does not parse is recorded with `data=None` and
`Error('invalid_plist', 'malformed plist; bytes withheld')`, never its raw bytes. Extend
`test_capture_roundtrip_and_environment_redaction` with a malformed plist containing an
`EnvironmentVariables` value string and assert that string appears nowhere in the emitted
archive bytes and that the plist entry carries the error.

## Important 2: a capture of an invalid registry fails its own replay (snapshot.py:219-222)

`validate_entries` requires a plist entry for every registry job even when `load_registry`
returned validation errors (duplicate project or identity). `capture_snapshot` skips the plist
join in that case and records no plists, so `load_snapshot` on that capture raises
`missing plist entry` and replay never reports the real registry errors. Require plist entries
(and the command set) only when the registry has no errors; with errors, replay must return the
registry-error report as the code at `replay` already intends. Add a test (in
`test_snapshot.py`) that captures a duplicate-identity registry with fake adapters, loads the
emitted archive, and gets a report whose errors name the duplicate.

## Definition of done

From `product/fleet_audit/`: `uv run python -m fleet_audit.acceptance registry --offline`
(`OK registry`), `uv run python -m fleet_audit.acceptance observer --offline` (`OK observer`),
`uv run --with pytest pytest -q` (zero failures). From the worktree root: `bin/lint` exit 0,
`rg -l '^(import|from) subprocess' product/fleet_audit/fleet_audit` prints only `collect.py`.
Final message under 20 lines: commit hash, the outputs, anything you could not do.
