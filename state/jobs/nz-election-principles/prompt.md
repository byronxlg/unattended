# Build: restyle the NZ election site against the design principles (issue #34)

Goal: Byron (issue #34) says the live site has bad colour, layout, too many collapsibles and
references flooding the main page. Implement `intent/nz-election/design-principles.md` in one
change. Read it first; it is the spec. Then `intent/nz-election/look-538.md` (tokens, type, still
binding where the principles do not change them), `REVIEW.md`, `AGENTS.md`.

Files to read first: product/nz_election/pipeline/build.py and the home/page templates it uses,
the CSS file, social_page.py, the methods page builder, tests that pin home structure
(grep tests for `details`, `source`, h2 text, route counts), screenshots.py.

Constraints:
- Move, never delete, provenance: every figure's full source detail (polls list, revision, fetch
  time, derivations such as Others-as-remainder) goes to a sources page (reuse methods/ or add
  `sources/` with one anchor per home module). Add a test that every figure id on home has an
  entry there. Adding a route moves the registered-route contracts (route count pins in tests and
  screenshots.py) with it, never weaker.
- Home: zero `<details>`; at most six modules in principle 3's order; one footnote line per module;
  hero per principle 1. Social POC, coalition statements and other modules become links in a
  closing "More" list (their routes stay, fragments that existed stay reachable on their routes).
- Bloc colours only on bloc-level data; notice yellow at most once per page.
- Tests on main at the base sha that pin old home structure (heading text, module count, details
  present, inline source chips on home) move to the new contract in the same commit; byte, font,
  contrast, axe, viewport and no-unsourced-figure checks keep or gain strength.
- No 538 marks, fonts or copy. No emojis, no em dashes.

Done when (report each command and its output in last.md; do not commit last.md):
- `uv run --with pytest pytest -q` all pass.
- `bin/lint` ok; the repo's verify all PASS; screenshot harness PASS on all routes.
- A measurement script (commit it under product/nz_election/tools/ or tests) prints for the built
  home: details 0, links under 60, "source" in rendered text under 12, HTML under 35 KB, h2 at most
  6 plus More. Print the numbers.
- Screenshots of home and the sources page at 360, 390 and 1280 in artifacts/ (not committed).
Commit on this branch; do not push.
