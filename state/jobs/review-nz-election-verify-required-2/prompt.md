Second fresh-context review of PR #81 (nz-election-verify-required), read-only. Worktree .worktrees/nz-election-verify-required,
branch change/nz-election-verify-required, head d2538ee on main 7ecf80a. Full diff: git diff 7ecf80a...d2538ee; the fix round
alone: git diff 617dd80 d2538ee. Judge against REVIEW.md; read product/nz_election/runbook/night.md "Deployed acceptance".

Goal: `verify.py all` never claims night/waterfall validation it skipped (prints SKIP), and `--require night,waterfall` makes an
absent night family fail (MISSING_NIGHT_FAMILY, nonzero exit) for release acceptance from 7 November.

The first review found: when night/index.json is listed in the manifest but absent, the missing-family code was lost (a
different error, nonzero exit). Check the fix: required-family presence is checked before bundle and site validation on every
path (all, explicit check, --site, --data, --site with --data, manifest lists the family but the file is absent, waterfall
present but night absent); the reason code and exit are MISSING_NIGHT_FAMILY in each; no regression to non-required runs
(SKIP lines, exit 0 when nothing is required); no existing test on main at 7ecf80a changed. Do not run pytest; read and
probe (small python -c probes are fine).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
