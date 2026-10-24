# Follow-up 3: close the campaign failure boundary structurally

Third fresh review of PR #75 (e905c50) requests changes, two Important; the supervisor read the
lines and agrees. Same invariant as follow-ups 1 and 2: a campaign failure message is an owned code
plus a fixed description, never text from upstream data or a forwarded exception string. Three
rounds have closed one exception type at a time; this round closes the boundary instead.

1. `product/nz_election/pipeline/campaign_checks.py:33` `INPUT_ERRORS` is an allowlist; RuntimeError,
   AssertionError, EOFError (for example from `gzip.decompress`) raised with upstream text escape the
   guard and reach a traceback. At the campaign reporting boundary (inside `verify_campaign`/
   `check_snapshots` and in `verify.cli`) catch `Exception` (not BaseException) and translate to an
   owned code (`CampaignError` keeps its code; anything else becomes `CAMPAIGN_DATA`). No traceback
   and no `str(exc)` for campaign or all.
2. `product/nz_election/pipeline/verify.py:495` `cli()` uses `sys.argv[1]` as the check name, so
   `verify.py --site X campaign` or `--site X all` skips redaction (reviewer got
   `FAIL --site: RAW_UPSTREAM_SENTINEL`). Use the parsed check (have `main` take argv or return the
   parsed args, or parse once in `cli`), and print that name.

Other single checks' messages stay as they are unless no test on main at bec0594 pins them.

Definition of done:
- Regressions: a RuntimeError and an EOFError carrying `RAW_UPSTREAM_SENTINEL` injected in the
  campaign path, through `check_snapshots()`/`verify_campaign` and through `cli()` exit text; and
  `cli()` with argv `['verify.py', '--site', <dir>, 'campaign']` and `... 'all'` under an injected
  read failure. Each asserts the marker absent, the code present, and the printed check name is
  `campaign`/`all`. Name in last.md one that fails on e905c50.
- `uv run --with pytest pytest -q product/nz_election` passes (say which Chromium-only failures your
  sandbox shows); `bin/lint` ok; `PYTHONPATH=. uv run python product/nz_election/verify.py campaign`
  PASS.
- Tests on main at bec0594 are not edited; this branch's own tests may move with the fix.
- Commit in the worktree, do not push, do not commit last.md.
