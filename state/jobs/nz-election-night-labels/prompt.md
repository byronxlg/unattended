# Build: night/ replay labels at 390 (design backlog 2026-10-26, item 3)

Page plan: intent/nz-election/pages/night.md
Design: product/nz_election/DESIGN.md (tokens and components; nothing new)

## Goal
On night/ at 390 px, two labels read wrong (supervisor design-loop critique, `state/design-backlog.md`):
1. The replay's reporting line says "updated 00:00" (`pipeline/night_page.py:48-50`, `clock[11:16]`). In replay mode a
   reader takes that as midnight. In replay and final-archive modes say what it is: the 2023 final count (frame N of M
   where that is the context); keep the clock only when a live feed supplied it.
2. The opposition bloc label "Labour, Green<br>and Maori" (`night_page.py:76`) wraps to three lines beside 55.
   Use the short bloc names home uses (Opposition, Government; read `pipeline/home.py` / `home_graphics.py` for the
   exact words and reuse the source rather than a second literal), with the parties named once elsewhere on the
   module if they are not already (an accessible name or the caption is fine).

## Read first
AGENTS.md, DESIGN.md, intent/nz-election/pages/night.md, pipeline/night_page.py, tests/test_night_page.py and
tests/night_*browser*.py (what they check), runbook/night.md.

## Constraints
- Presentation and copy only: no data shape, pipeline or workflow change. Files outside night_page.py and its
  template/CSS only if the shared bloc names need a small export.
- Tests check data, provenance, absence and accessibility; never pin markup, class names or bytes. Tests on main
  that assert the old wording ("updated", "Labour, Green") move with this change: a build round, not a fix.
  Add one behaviour test: a replay row renders no bare clock time presented as an update time.
- No emojis, no em dashes. Commit in the worktree, do not push.

## Done
- `uv run --with pytest --with playwright pytest -q product/nz_election/tests -k night` passes (browser cases may be
  sandbox-denied; say which).
- `bin/lint` ok.
- last.md lists files changed, the before and after strings for both labels, and the test output tail.
