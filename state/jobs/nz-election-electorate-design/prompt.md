# Build: electorate pages on the design system

Design system: product/nz_election/DESIGN.md (read it first; tokens and components to build from).
Page plan: intent/nz-election/pages/electorate.md (what the page answers and in what order).

## Goal
`electorates/<slug>/` (71 pages) is the top item in `state/design-backlog.md`: since the 26 Oct redesign
home, polls, vote, parties and night use the DESIGN.md anatomy; electorate pages still have the
pre-redesign layout. Bring them onto the system, keeping the page plan's order and every fact they
show today (candidates, enrolment check, Policy.nz link, 2023 result, night state).

1. Hero: kicker (region or "Maori electorate"), h1 the electorate name, one-sentence answer (who holds
   it and by how much in 2023, labelled when boundaries changed), and the locator: the shared hex map
   (`home_graphics.hex_map`, the hex-native layout once PR #97 is on main) at card size with this seat
   highlighted and focusable, not a new map style.
2. Candidates as race cards (page plan Graphics 1): party colour bar, name large, party, list rank,
   incumbent tag; photos only where a licensed portrait already exists in `snapshots/`.
3. 2023 result as thick horizontal bars in party colours with direct labels and the margin annotated
   (Graphics 4), replacing any table-only view; the table stays available for accessibility if the
   page has one today.
4. Enrolment line and Policy.nz link as DESIGN.md source/action components, kept above the fold at 390
   with question 1.

## Read first
`AGENTS.md`, `REVIEW.md` (pass 4 is by eye), DESIGN.md, the page plan, `pipeline/electorate_pages.py`,
`pipeline/home_graphics.py`, `web/electorate.css`, `web/electorates.mjs`, `tests/test_electorates.py`,
`tests/test_electorate_page_plan.py`, `tests/test_electorate_policy_links.py`.

## Constraints
- Colours only through tokens (`var(--p-...)`, `pc()`); type only from the existing type tokens (16 px
  reading floor, SVG labels at least 12 px at 360); no new font sizes.
- Data, provenance, absence and accessibility checks stay; tests on main at the base sha that pin old
  markup or class names (not data) may move to the new markup; name them in last.md.
- Never print "not available" style text (absent means absent); the absence gate stays green.
- `test_design.py` and every `test_home*.py` stay green (the hex map is shared with home).

## Done when
- `uv run --with pytest pytest -q product/nz_election` passes (say which failures are Chromium launch
  denials in the sandbox), `bin/lint` passes.
- Screenshots at 1280x900 and 390x844 of three electorates (one general, one Maori, one with changed
  boundaries) listed in last.md (`uv run --with playwright python product/nz_election/tests/screenshots.py
  --site site --out artifacts/nz-election/screenshots`). No horizontal scroll at 390; candidates visible
  in the first screen at 390.
