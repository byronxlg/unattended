# Fix: Fleet Audit increment 5, third fresh review finding

Same worktree `.worktrees/fleet-audit-5`, branch `change/fleet-audit-5`, HEAD e2c946e. Commit in
the worktree; never push. Fixtures unchanged. Under `tests/` you may edit exactly one existing
assertion (named below, added in e2c946e at the supervisor's instruction, which was wrong) and
add one new test function to `tests/test_reports.py`; nothing else under `tests/`.

## Important: the mtime conversion failure shape cannot round-trip through a snapshot

e2c946e reports a `ValueError`/`OverflowError` from `datetime.fromtimestamp` as `exists=True`,
`mtime=None`, `stat_error` set. `snapshot.py` `output_observation` line 323 rejects that
combination as `inconsistent output evidence`: its invariant is that `exists True` implies a
known mtime and no error, and any stat error implies `exists` not True. So `capture` would
write a snapshot that `replay` refuses, turning a recorded observation failure into invalid
input. The supervisor dictated `exists True`; the invariant in the validator is the right one
and the existing branch already uses `exists None` for every stat error that is not
`FileNotFoundError` (permission denied, not a regular file), where the file may well exist.
Fix: in `files.py` `stat_output`, drop the special case so a conversion failure reports
`exists None`, `size None`, `mtime None`, `age_seconds None`, `stat_error` set, exactly the
shape of the existing non-missing error branch. Do not change `snapshot.py`. In
`test_output_mtime_out_of_range_is_uncertain` change `observation.data.exists is True` to
`observation.data.exists is None`; nothing else in that test. Add
`test_output_mtime_out_of_range_round_trips_snapshot` that serialises the observation with
`reports.serialize` and passes it through `snapshot.output_observation(row, path)` asserting
the result equals the original observation (or, if `observed_at` or another field cannot be
equal by construction, assert `data` and `error` equal and say why in a one-line comment).

## Definition of done

From `product/fleet_audit/`: the five acceptance stages (`registry`, `observer`, `verdicts`,
`drift`, `fleet`, each `uv run python -m fleet_audit.acceptance <stage> --offline`, last line
`OK <stage>`), `uv run --with pytest pytest -q` (zero failures, 316 or more tests),
`git diff --stat e2c946e` touching only `fleet_audit/files.py` and `tests/test_reports.py`,
with `git diff e2c946e -- tests/` showing one changed assertion line plus one new function.
From the worktree root: `bin/lint` exit 0. Final message under 15 lines: commit hash, the
outputs, anything you could not do.
