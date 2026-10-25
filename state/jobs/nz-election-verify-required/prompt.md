# Build: verify.py all must say what it skipped, and refuse to skip when told the family is required

Change: nz-election (plan-week-after.md, "7 November readiness": "`all` can skip absent night/waterfall families").
Read first: `AGENTS.md`, `intent/nz-election/plan-week-after.md` (readiness section, increment 4),
`product/nz_election/pipeline/verify.py` (main(), the loop near the comment "The aggregate gate
permits absent families"), `product/nz_election/runbook/night.md`, the tests that run `verify.py all`
(`rg -n "verify.py|verify\.main|'all'" product/nz_election/tests`).

## Problem
`verify.py all --data <bundle>` silently `continue`s past night and waterfall when the bundle has no
`night/index.json`, then prints `PASS all`. Before 7 Nov that is correct (no live family yet). On and
after election night, the release acceptance (increment 4) reads `PASS all` as proof the night
family validated; an absent or lost night family would pass unseen.

## Goal
1. Every skipped check is visible: `all` prints `SKIP <name>: family absent (night/index.json)` for
   each family it skips, on stdout, and `PASS all` stays the last line only when nothing required
   was skipped.
2. A way to make the family required: a `--require <name>[,<name>]` option (names from the existing
   checks; unknown name is an input error with the existing redaction path in `cli()`), under which
   an absent family fails with the existing `MISSING_NIGHT_FAMILY` code and nonzero exit instead of
   being skipped. Default behaviour (no `--require`) is unchanged except for the SKIP lines.
3. Runbook: `product/nz_election/runbook/night.md` acceptance steps for 7 Nov onward use
   `--require night,waterfall`; one sentence saying why.

## Constraints
- No workflow file changes (pages.yml stays as is; the night acceptance is run by hand by the
  supervisor). No page or template changes.
- Tests on main at base sha 7ecf80a may gain assertions only where they pin the exact stdout of
  `all` and the new SKIP line moves it; say which in last.md. Nothing weakens a check.
- New tests: absent family without `--require` prints SKIP and PASS all (exit 0); with
  `--require night` exits nonzero with MISSING_NIGHT_FAMILY and no `PASS all`; present family with
  `--require night,waterfall` runs both checks (use an existing fixture bundle the night tests use).
  The `--require` test must fail on 7ecf80a.
- Commit in the worktree, do not push. Do not commit last.md.

## Done
- `uv run --with pytest pytest -q product/nz_election/tests/test_verify*.py product/nz_election/tests/test_night_operation.py` passes (name the files you actually used if different).
- `bin/lint` prints ok.
- In last.md: the commit sha, test counts, the exact stdout of `verify.py all --data <a bundle without night>` and of the same with `--require night` (exit code shown).
