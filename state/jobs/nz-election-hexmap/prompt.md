# Build: hex-native electorate layout on the home map

Design system: product/nz_election/DESIGN.md (hex map component). Page plan: intent/nz-election/pages/home.md.

## Goal
Replace `product/nz_election/snapshots/hexmap.json` records with the hex-native layout researched in
`state/jobs/research-nz-election-hexmap/last.md` (file ready at `state/jobs/nz-election-hexmap/hexmap.json`, copy it
from the main checkout: 71 slugs, 71 unique cells, odd-r pointy-top, neighbour agreement 76/101 old to 106/138 new).
`pipeline/home_graphics.py` `hex_map` must draw it as true hexagons (odd rows offset half a column east), with the
Maori cluster to the right, labels and targets as today.

## Read first
`AGENTS.md`, `REVIEW.md`, DESIGN.md, `pipeline/snapshots.py` (hexmap validator around :242 and :298-312),
`pipeline/home_graphics.py` `hex_map`, tests that read hexmap (`rg -l hexmap product/nz_election/tests`).

## Constraints
- The validator stays as strict as now (every electorate exactly once); add a check that no two cells share coordinates
  if none exists. Keep `source_url`, `licence`, `retrieved_at` per record.
- Tests that pin old coordinates move with the new layout; say which in last.md. No markup or byte pins.
- Map targets stay at least 24 px at 390 and 360 (existing harness checks).

## Definition of done
- `uv run --with pytest pytest -q product/nz_election/tests/test_snapshots*.py product/nz_election/tests/test_home*.py product/nz_election/tests/test_design.py` passes.
- `bin/lint` ok; `uv run product/nz_election/pipeline/verify.py all` PASS on a fixture build.
- Home screenshots at 390 and 1280 in last.md paths; North Island reads as one shape, South Island contiguous.
