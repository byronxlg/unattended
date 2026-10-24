# Follow-up 2: two more paths that echo data into campaign failures

Second fresh review of PR #75 (7f027fb) requests changes, two Important; the supervisor read the
lines and agrees. Same invariant as follow-up 1: a campaign failure message is an owned code plus a
fixed description, never text from upstream data or a forwarded exception string.

1. `product/nz_election/pipeline/verify.py:344` `verify_campaign` calls `export.validate_bundle(data)`
   and lets its ValueError through; the reviewer got
   `ValueError: INVALID_TIMESTAMP: envelope.data.RAW_UPSTREAM_SENTINEL.observed_at` (a data key in the
   message). The CLI's supplied-bundle validation at line 431 does the same before any check runs,
   and line 494 forwards `str(exc)` into the exit text. Fix it for `verify.py campaign` and for
   `verify.py all` (which runs campaign) with `--data`: the exit text carries no data-derived text.
   Leave other single checks' messages as they are unless the change is the natural shared fix and
   no test on main at bec0594 pins them; if one does, stop and report rather than edit it.
2. `product/nz_election/pipeline/campaign_checks.py:94` `labels[row.attrib['p_no']]` raises
   `KeyError: 'RAW_UPSTREAM_SENTINEL'` for an unknown p_no, before the owned check; the CLI catches
   only ValueError, so it becomes a traceback. Normalize to `OFFICIAL_ERRORS` (the CAMPAIGN code).
   Look for the same lookup shape (dict index, `.attrib[...]`, `int(...)` on upstream values)
   elsewhere in campaign_checks.py and treat it the same.

Definition of done:
- Marker regressions for both paths (supplied bundle with a sentinel key through `verify_campaign`
  and through the CLI `main()` exit text; unknown p_no through `check_snapshots()`), asserting the
  marker is absent and the code present; name in last.md one that fails on 7f027fb.
- `uv run --with pytest pytest -q product/nz_election` passes (Chromium-only failures in your sandbox
  are known; say which); `bin/lint` ok; `PYTHONPATH=. uv run python product/nz_election/verify.py
  campaign` PASS.
- Tests on main at bec0594 are not edited; this branch's own tests may move with the fix.
- Commit in the worktree, do not push, do not commit last.md.
