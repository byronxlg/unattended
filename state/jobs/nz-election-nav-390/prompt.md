# Build: the site header nav fits one row at 390 px

Page plan: intent/nz-election/pages/home.md (the header sits above every page's first answer; the plan puts
the answer first, and a two-row header at 390 pushes it down on every route).
Design: product/nz_election/DESIGN.md (tokens and components; the 16 px reading floor binds).

## Goal

At 390 px wide the masthead nav wraps to two rows (Overview Polls Parties Funding / Electorates Vote Night,
Methods), so the header takes about 160 px of the first phone screen on every route. Make the header one row
of links at 390 (and at 360 if it fits without breaking the rules below), with every route still reachable from
every page. Top item of state/design-backlog.md (critique 2026-10-26 20:15Z item 1, repeated 27 Oct 07:55Z).

## Read first

- product/nz_election/DESIGN.md (header component), product/nz_election/web/styles.css (body>header nav,
  about lines 300 to 306), wherever the nav links are rendered (rg for the link set in pipeline/).
- state/design-backlog.md top entries.
- Tests that touch the header: rg -n "header|nav" product/nz_election/tests/test_design.py
  product/nz_election/tests/screenshots.py (HEADER_TARGET_BOUNDS and the 44 px target checks).

## Constraints

- Options, your choice: shorter labels (Overview to Home, for example), Methods moved to the footer with a
  footer link on every page, or a horizontally scrollable single row with a visible cue. Not allowed: type
  under the 16 px floor, targets under 44 px, links that become unreachable, a JavaScript menu.
- Keyboard and screen-reader behaviour unchanged: one nav landmark, aria-current on the active route.
- Tests check behaviour (header height at 390, every route linked, target sizes), not markup or class names.
  Contracts that pin the old label set or link count move with the new set; nothing weaker.
- This branch stacks on change/nz-election-parties-credit (which stacks on the funding page); do not touch
  funding_page.py or parties_page.py.

## Done when

- A test that fails on the base commit and passes now: at 390 the header nav occupies one row (header
  height under about 100 px) and every route in the registered set is linked from home (header or footer).
- `uv run --with pytest pytest -q product/nz_election/tests -k "design or home or nav or header"` passes
  apart from sandbox-denied Chromium launches (list them by name in last.md; the supervisor runs them on
  the host).
- `bin/lint` prints `lint ok`.
- Commit in the worktree, do not push. last.md says what changed, the option chosen and why.
