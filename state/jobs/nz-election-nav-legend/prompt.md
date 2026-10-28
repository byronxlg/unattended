# Build: header nav and home seat legend at 390

Page plan: intent/nz-election/pages/home.md (home's seat legend); the header is sitewide.
Design: product/nz_election/DESIGN.md (tokens and components; follow it).

Goal: two presentation defects from state/design-backlog.md (2026-10-27 20:56Z critique), deployed site at 390:
1. Header nav at 360 and 390 still shows a clipped "Electora" with a trailing chevron after PR #108. A reader
   must see whole link labels: every nav link either fully visible or reachable by an obvious scroll affordance
   that does not cut a word mid-label on first view. Keep every route in the nav; no hamburger menu (removed
   in PR #36 by decision). Focus visibility and 44 px targets (main's HEADER_TARGET_BOUNDS, FOCUS_NOT_VISIBLE
   checks) must keep passing.
2. Home seat legend at 390 leaves "TOP 7" alone on its own row between the two bloc rows. Legend entries should
   group by bloc so no party sits orphaned between blocs (pipeline/home_graphics.py or the template).

Read first: AGENTS.md, DESIGN.md, product/nz_election/styles.css (header rules), product/nz_election/tests/test_design.py
(header checks), pipeline/home_graphics.py (legend).

Constraints: tests check behaviour and accessibility, never markup, class names or byte counts. Tests on main at
the base sha may not be weakened; add a check that fails on the base for item 1 (no nav label clipped at 360/390,
measured by bounding boxes) if it fits the existing harness.

Done when:
- `uv run --with pytest pytest -q product/nz_election/tests -k "design or home or header or nav"` passes except
  Chromium sandbox-launch denials (list them; the host runs those).
- `bin/lint` prints `lint ok`.
- Commit in the worktree; do not push; do not commit last.md. Report the commit and which screenshots you could
  not take.
