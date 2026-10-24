# Build: polls page refinement round (nz-election-polls-refine)

Page plan: intent/nz-election/pages/polls.md

Goal: three reader-visible defects on polls/ (merged in PR #71, 170bf94), no new content.

1. The Opportunity Party shows as "OPP" (the Wikipedia column header) wherever a party label is
   drawn (polls/ hero strip "OPP 7", legends, tables, home seat bar if the same helper is used).
   Readers know it as TOP. Map the source header to the reader label in one place (where party
   ids become display labels); the parser keeps reading the OPP column (poll_parser.py:236
   signature and its tests stay as they are).
2. On polls/ at 1280 the National segment of the hero strip is drawn as two adjacent blue blocks
   (total 43). Find why (sub-split, duplicate series, rounding remainder) and draw one segment per
   party. Add a check that fails on 170bf94: each party appears at most once per strip.
3. Nit: the "since <date>" text in the change summary renders smaller than its sentence; same size.

Read first: AGENTS.md, REVIEW.md pass 4, intent/nz-election/pages/polls.md,
intent/nz-election/design-principles.md, product/nz_election/tests/screenshots.py.

Constraints: no edits to tests on main at 170bf94 except where a pinned "OPP" display string must
move to "TOP" (say which in last.md); nothing weaker. Absent-text rule (#40) holds. Commit in this
worktree, do not push.

Done when:
- `uv run --with pytest pytest -q product/nz_election` passes (Chromium tests may skip in your
  sandbox; say so).
- `bin/lint` prints ok.
- The new strip check fails on 170bf94 and passes on HEAD (show both outputs in last.md).
- The supervisor runs `screenshots.py --site <build>` on the host (must print PASS screenshots)
  and looks at polls/ 390 and 1280 for TOP and a single NAT block.
