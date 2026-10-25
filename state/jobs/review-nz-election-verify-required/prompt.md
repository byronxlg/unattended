Fresh-context review of PR #81 (nz-election-verify-required), read-only. Worktree .worktrees/nz-election-verify-required,
branch change/nz-election-verify-required, head 617dd80 on main 7ecf80a. Diff: git diff 7ecf80a...617dd80. Judge against
REVIEW.md; read product/nz_election/runbook/night.md "Deployed acceptance" and intent/nz-election/plan-week-after.md.

Goal: `verify.py all` must never claim night/waterfall validation it skipped (now prints SKIP lines), and
`--require night,waterfall` must make an absent night family fail (MISSING_NIGHT_FAMILY, nonzero exit) for release
acceptance from 7 November.

Check: every path where night or waterfall can be skipped or absent while --require names it fails (all, explicit check,
--site without --data, --data without night/index.json); --require with a single check and with an unknown name;
cli() reason and exit code for MissingNightFamily vs the campaign/all redaction path (an absent family must not be
reported as a campaign DATA error); --require on a non-night name runs that check rather than silently passing; no
existing test changed. Do not run pytest; read and probe (small python -c probes are fine).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
