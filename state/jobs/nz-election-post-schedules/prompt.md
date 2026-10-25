# Build: post-election schedules and copy (plan-week-after increment 3)

Page plan: intent/nz-election/pages/home.md (also pages/vote.md for the vote/ copy; copy changes by phase only, no new modules, no layout change).

## Goal

Every election cron runs forever and home/vote/share copy still invites voting after 7 November. Byron accepted (NOTE closed on silence 2026-10-25 12:45Z) these policies:

1. Hourly poll acquisition stops at 2026-11-07T06:00:00Z (polls close 19:00 NZDT).
2. The five-minute night loop stops at 2026-11-08T06:00:00Z (already `night_live.CLOSE`; reuse it, do not duplicate it).
3. Social daily continues to 2026-11-14 (last budget day 14 Nov NZ), its caption names the sample period, including that post-election days are in it; no paid call after the sunset.
4. Daily collection (candidates, markets, advance and the rest in `nz-election-daily.yml` / `daily_sources.py`) runs to 2026-11-14, then stops scheduled collection; manual `workflow_dispatch` stays possible for the 27 Nov official import and a manual Pages deploy.
5. Disabling hourly removes social's rebuild mechanism (runbook.md:217): keep a deployment after each social publish through 14 Nov (daily build or an explicit Pages trigger, your choice), proven by a test.

Invariants (choose the mechanism): each sunset is one named constant in one module that workflows and loaders read; a scheduled run after its sunset exits 0 with a one-line log and makes no network or paid call; the publication freeze (6 Nov 23:30 NZDT to 7 Nov 19:00) is untouched.

Copy by phase (build-time clock, injectable): after 2026-11-07T06:00Z, no route invites the reader to vote or find a voting place; home/share title "New Zealand votes on 7 November" and "Who is standing" become past-tense equivalents; night metadata describes current preliminary results, not a replay; vote/ voting-place and help actions are replaced by where to find results (night/) and the official-results date 27 November. Follow the existing absent-text gate (no "not available" wording). Locations: route_cards.py:30/36/44, home.py:381, vote_page.py:38/42/51 (from plan-week-after.md; verify).

## Read first

AGENTS.md, intent/nz-election/plan-week-after.md (8 to 14 November, increment 3), pages/home.md, pages/vote.md, .github/workflows/nz-election-{hourly,daily,social-daily}.yml, pages.yml, pipeline/daily_sources.py, deployment_guard.py, night_live.py, social workflow code, route_cards.py, home.py, vote_page.py, product/nz_election/runbook.md, runbook/night.md, tests/test_workflows.py, test_night_operation.py.

## Constraints

- Tests on main at the base sha are protected except those that pin the old copy or unbounded schedules; name each in last.md with the reason. Contracts move with the copy (grep tests for each string you change). This branch's own tests move with it.
- Injected clocks only; no sleeps, no network.
- Runbook: one section "Sunsets" listing every constant, its value, how to move it, and how to run a manual collection after it.

## Done

- Injected-clock tests at 7 Nov 05:59:59Z / 06:00Z, 8 Nov 06:00Z, 14 Nov end, 27 Nov: each workflow's guard decision, zero paid calls after the social sunset, the social-deploy path, and copy for each route above.
- `uv run --with pytest pytest -q` whole suite: report counts; browser tests may fail in the sandbox on Chromium launch, say which.
- `uv run product/nz_election/pipeline/verify.py all` PASS; `bin/lint` ok.
- Screenshots of home/ and vote/ at 390 and 1280 built with the clock at 2026-11-08T00:00Z, paths in last.md.
- Commit in the worktree, do not push. last.md: what changed, constant locations, test counts.
