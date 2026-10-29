# Build: scheduled shutdown is not a failure on polls/ and the markets panel

Page plan: intent/nz-election/pages/polls.md (and pages/home.md for the markets panel). Look and
components: product/nz_election/DESIGN.md. Copy only; no layout change.

## Goal

After the hourly (polls) and daily (markets) collections stop on their scheduled sunsets
(`product/nz_election/pipeline/sunsets.py`: `ended(kind)`, `allowed(kind, now)`), the site still
says "Update overdue" (`pipeline/build.py:280`, polls/) and "Update overdue or failed"
(`pipeline/market_panel.py:60`). The home banner already handles this (PR #131); these two
surfaces do not. A reader on 8 Nov should see "Scheduled updates ended" with the date of the
last retained observation, not an alarm.

## Invariants

- The sunset times come from `sunsets.py` only; no new literal timestamps.
- Past the sunset, a final collection that succeeded shows the ended wording plus the retained
  observation date. A genuinely failed last run (status row not ok) before the sunset still shows
  the overdue/failed wording; past the sunset it shows the ended wording and keeps the failure
  visible as a separate plain line (do not hide that the last update failed).
- Before the sunset, behaviour is unchanged.

## Read first

`pipeline/sunsets.py`, `pipeline/build.py` around 260-300, `pipeline/market_panel.py`, how
PR #131 did it on home (`git log --oneline -S "Scheduled updates" -- product/` and that diff),
tests `test_sunsets.py`, `test_polls_plan.py`, `test_markets.py`.

## Tests

Add renderer assertions (data and wording, not markup or class names) at five clocks:
7 Nov 06:00Z, 7 Nov 10:00Z, 8 Nov 06:01Z, 14 Nov 00:00Z, 27 Nov 00:00Z, each with a healthy final
collection and a failed one. Tests on main at the base sha are protected except an assertion
that pins the old overdue wording past a sunset: that contract moves with this change; name it
in last.md. New cases must fail on origin/main's code.

## Done

`uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py product/nz_election/tests/test_polls_plan.py product/nz_election/tests/test_markets.py product/nz_election/tests/test_home_failed.py` 0 failed;
`bin/lint` ok. Commit in the worktree; do not push. last.md: files, the moved contract if any,
the new cases that fail on base.
