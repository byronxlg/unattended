# Build: preliminary, settled and official result states (week-after increment 2)

Page plan: intent/nz-election/pages/night.md
Plan: intent/nz-election/plan-week-after.md, increment 2 and the "8 to 14 November" section.

Branch change/nz-election-results-states stacks on change/nz-election-night-start (PR #78, open). Do not edit
bin/tick, bin/night-watchdog or pipeline/night_start.py; those belong to #78.

## Goal

After election night the site must say plainly what state the results are in, and never look broken:

1. Live (as now): "Live preliminary results", polling every cycle.
2. Settled: live updates ended, the last complete preliminary capture retained and dated. The client stops
   polling and shows "Preliminary results, final count 7 November <time>; official results due 27 November"
   (exact wording yours, keep it a sentence a reader understands). Accept this state in night-live.mjs
   (it currently accepts only "Live preliminary results" and polls forever, web/night-live.mjs:33, :76).
3. Official: an import path for the EC official result (same XML family as the preliminary feed, fixtures only;
   no network capture, the 27 Nov capture is a human step). Pin the final preliminary package as a baseline so
   official vs preliminary comparison (pipeline/night_seats.py:16) has a compatible pair. Specials: never label
   official minus preliminary as "special votes"; show a specials component only when the source states it.

Home (pipeline/home.py:165, :382) follows the same state: results-first in any of the three states, with the
state sentence in the hero. Government formation caveat stays separate.

## Read first

REVIEW.md, AGENTS.md, intent/nz-election/pages/night.md, intent/nz-election/design-principles.md,
product/nz_election/pipeline/night_live.py, night_page.py, night_seats.py, home.py, web/night-live.mjs,
product/nz_election/runbook/night.md, tests/test_night_operation.py, tests/test_night_page.py, tests/test_home_plan.py.

## Constraints

- Absent means absent: no "not available" copy; the ABSENT_TEXT and night absent-text gates stay as they are.
- The s197 freeze and night_live.require_open bounds are unchanged.
- Contracts that move with a new state (registered families, state enums, pinned copy) move with it; this is a build,
  not a fix. Nothing weakens a check.
- No new dependencies. Dated fixtures for preliminary-final and official under the existing fixture tree.

## Definition of done

- Tests for each state transition (live to settled, settled to official, absent feed, baseline pinned) and a client
  test that settled stops polling, plus a regression shown failing on the base commit.
- `uv run --with pytest pytest -q product/nz_election/tests` all pass (host runs the browser tests too).
- `uv run product/nz_election/pipeline/verify.py night` PASS and `verify.py waterfall` PASS.
- Runbook night.md: how to move to settled and how to run the official import, exact commands.
- `bin/lint` prints lint ok.
- Screenshots of night/ and home at 390 and 1280 in each of settled and official, under artifacts/ (untracked),
  listed in last.md with the question test from pages/night.md answered for each.
- Commit in the worktree; do not push. last.md: what changed, the commands and their output, anything not done.
