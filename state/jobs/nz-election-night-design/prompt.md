# Build: election night page on the design system

Design system: product/nz_election/DESIGN.md (read it first; tokens and components to build from).
Page plan: intent/nz-election/pages/night.md (what the page answers and in what order).

## Goal
`/night/` is the page readers will have open on 7 November. Since the 26 Oct redesign (PR "Redesign:
design system, home, polls, electorates, vote, parties"), every other public page uses the DESIGN.md
anatomy and components; night still has the old look: a flat seat strip, a list of majority
combinations as bullets, a mono table of leaders, a small square-ish hex map. Bring it onto the system
without changing what the live client does.

1. Hero: kicker (the result state, e.g. "Replay of 2023" before the night, "Live" on the night), h1
   "Who is winning?", a one-sentence answer, and the seat hemicycle (`home_graphics.hemicycle` or a
   variant fed by the night seat totals) with big bloc numbers, replacing the strip.
2. Majority combinations: a compact grid of cards (parties as colour chips, seat total big, a mark when
   it reaches the majority), not a bullet list.
3. Electorate map: reuse `home_graphics.hex_map` styling (size, tones, focus state, map key) so the two
   maps look the same; colour by provisional leader.
4. Leaders table: the poll-table look from DESIGN.md (tinted party cell, sticky first column, display
   names in title case where the source gives SURNAME, Given).
5. Countdown/pre-night state uses the ribbon and timeline components.

## Read first
`AGENTS.md`, `REVIEW.md` (pass 4 is by eye), DESIGN.md, `pipeline/night_page.py`, `pipeline/night_electorates.py`,
`web/night.css`, `web/night.mjs`, `web/night-live.mjs`, `web/night-seats.mjs`, the night tests.

## Constraints
- The live client (`night-live.mjs`, `night.mjs`) must keep working: the DOM hooks it updates move with
  the markup; update its tests in the same change. Python and browser parity tests stay green.
- Colours only through tokens (`var(--p-...)`, `pc()`); no literals.
- Tests on main at the base sha that pin old markup or class names (not data, provenance, absence or
  accessibility) may be updated to the new markup; say which in last.md.

## Done when
- `uv run --with pytest pytest -q product/nz_election` passes, `bin/lint` passes.
- Screenshots at 1280x900 and 390x844 of `/night/` in the replay state and the live demo state
  (`uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots`),
  paths listed in last.md. No horizontal scroll at 390.
