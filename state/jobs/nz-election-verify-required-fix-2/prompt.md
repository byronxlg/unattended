# Fix-2 on PR #81 (verify-required), same branch, same worktree

Second fresh review, one Important, confirmed by the supervisor at
product/nz_election/pipeline/verify.py:432-440:

When both `--data` and `--site` are supplied, the missing-family presence check (night/index.json)
looks only at `--data`. If the data bundle has night but the site's data directory (the one the
site's build-manifest lists) lacks `night/index.json`, site validation fails with `CAMPAIGN_DATA`
instead of `MISSING_NIGHT_FAMILY`.

Invariant: whenever night or waterfall is the check or is in `--require`, every supplied location
(`--data`, and the site's data directory derived from `--site` as the code does now) is checked
for `night/index.json` before any validation, and a missing one raises MissingNightFamily (exit
nonzero, code MISSING_NIGHT_FAMILY). Optional (not required) behaviour is unchanged: SKIP lines,
exit 0.

Constraints: fix job. Tests on main at base 7ecf80a are untouched; this branch's own tests
(test_verify_missing_index.py and the other one it added) may gain cases. Add a regression for the
combined-flags case (bundle present, site data absent) that fails with verify.py at d2538ee.

Done when, in this worktree:
- `uv run --with pytest pytest -q product/nz_election/tests/test_verify_missing_index.py` passes
  and the new case fails with verify.py at d2538ee;
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_operation.py` passes;
- `bin/lint` ok. Commit on the branch, do not push, do not commit last.md.
