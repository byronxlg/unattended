# Fix: Fleet Audit increment 5, second fresh review findings

Same worktree `.worktrees/fleet-audit-5`, branch `change/fleet-audit-5`, HEAD d00b16b. Commit in
the worktree; never push. Existing tests and fixtures stay as they are; you may add new test
functions to `tests/test_reports.py` for the two findings below, nothing else under `tests/`.
`tests/conftest.py` unchanged. No fixture under `fixtures/` changes: the real-twelve rows that
carry KeepAlive mappings (com.koekeishiya.skhd, running; com.koekeishiya.yabai, disabled)
already hold output uncertainties, so their verdicts and the exit code 1 stay as expected.json
says. If a fixture would have to change, stop and say so instead.

## Important 1: scan drops Unsupported plist values from uncertainties (scan.py scan_fleet)

d00b16b carries plist `field_errors` into uncertainties, but a plist field that parsed to
`Unsupported` (today only `KeepAlive` set to a mapping, plists.py line 49: `Unsupported(raw,
"KeepAlive mappings are unsupported")`) still contributes nothing. Replaying the running
homebrew.mxcl.ollama row with `KeepAlive={"SuccessfulExit": false}` gives `uncertainties=[]`,
summary `uncertainties` 0, no text `uncertainty:` line and exit 0, while the evidence retains an
`Unsupported` policy the tool could not interpret. Audit surfaces the same value through an
unknown comparison (reports.py line 125 appends incomplete comparisons); scan has no
comparisons, so it must surface it itself. Fix, scan only: in `scan_fleet`, after the field
errors, append `plist: {Key}: {reason}` for every `Unsupported` value among the PlistData fields
and its `Schedule` fields (write a small helper that walks the dataclass fields generically,
mapping the field name to the plist key it came from where one exists, so a future Unsupported
field is covered without another edit). Deduplicate against existing entries with the
`dict.fromkeys` shape already used in output.py. Verdict unchanged (rule order untouched).
Audit behaviour unchanged. Add `test_scan_unsupported_plist_values_are_uncertain`: take the
real-twelve snapshot, inject a plist with a KeepAlive mapping on a running row through a
`SnapshotFiles` subclass the way `test_scan_plist_field_errors_are_uncertain` does, assert the
uncertainty line is present in the job and in `render_text`, the summary count is nonzero and,
with every other row filtered out or the exit computed for that job alone, the exit is 2.

## Important 2: output mtime conversion only catches OSError (files.py stat_output)

`datetime.fromtimestamp(info.st_mtime, timezone.utc)` raises `ValueError` for
253402300800 (year 10000) and `OverflowError` for 1e20; reproduced with the venv python. Only
`OSError` is caught, so a hostile or corrupt mtime loses the whole scan report. Fix: catch
`(OSError, ValueError, OverflowError)`; for the two conversion errors return the same
stat-error observation shape as the existing branch with `Error('stat', str(exc))` and
`exists` True (the stat itself succeeded; the timestamp is what failed). Add
`test_output_mtime_out_of_range_is_uncertain` that monkeypatches `os.stat` (or `fleet_audit.files.os.stat`)
to return a stat result with `st_mtime=253402300800` and asserts `stat_output` returns an
observation with `error.kind == 'stat'`, `data.exists is True`, `data.mtime is None`; repeat
for `1e20` in the same test.

## Definition of done

From `product/fleet_audit/`: the five acceptance stages (`registry`, `observer`, `verdicts`,
`drift`, `fleet`, each `uv run python -m fleet_audit.acceptance <stage> --offline`, last line
`OK <stage>`), `uv run --with pytest pytest -q` (zero failures, 315 or more tests),
`git diff --stat d00b16b` touching only `fleet_audit/scan.py`, `fleet_audit/files.py` and
`tests/test_reports.py`. From the worktree root: `bin/lint` exit 0; `rg -l '^(import|from)
subprocess' product/fleet_audit/fleet_audit` prints only `collect.py`. Final message under 20
lines: commit hash, the outputs, anything you could not do.
