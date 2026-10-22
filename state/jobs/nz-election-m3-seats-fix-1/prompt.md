# nz-election-m3-seats fix-1 (PR #62, follow-up on your build thread)

The fresh review of PR #62 requested changes. Fix these on change/nz-election-m3-seats in this worktree, commit, do not push.

1. Maori electorates clipped: `pipeline/night_electorates.py:81` lays the seven Maori electorates at x=15, so their polygons reach 451-479 px, outside the 450-wide viewBox. Make every electorate polygon sit inside the viewBox (widen it or move the column) and add a test that asserts every polygon's points lie inside the viewBox for the registered layout. Show that test failing on 467512b.
2. Reported ties lose their margin: `pipeline/xml_parser.py:157` and `web/night-parser.mjs:102` return leader=None, margin=None for a 100-100 count with all places counted, and `night_electorates.py:58` then says "Not yet reported". A reported tie has margin 0 and must read as a tie (say who is tied), in both parsers, with Python/JS parity covered. Leader may stay None if you show "Tied" by name. Add regression tests in both implementations.
3. Hex targets too small: hexagons render about 17x18 px in `web/night.css`. Each electorate must be selectable with a target of at least 24x24 px at 360 px viewport, either by larger hexes or by an adequately sized selection control (the searchable table already exists; the map links may then be aria-hidden duplicates only if the table is the accessible route). Extend the screenshot target check so the chosen route is covered rather than excluded.
4. Nit: `runbook/night.md:88-94` still says 20 images and no electorate map or table; make it match the 44-image registry and the implementation.

Tests: tests on main at the base sha are protected and must not be weakened; this branch's own tests move with the change.

Done when: `uv run --with pytest pytest -q product/nz_election/tests` passes except Chromium launch errors in your sandbox (name them), `PYTHONPATH=. uv run python product/nz_election/pipeline/verify.py all (as you ran it before)` ends PASS all, `bin/lint` prints lint ok, and last.md lists each item with the test that proves it and its result on 467512b. Do not commit last.md.
