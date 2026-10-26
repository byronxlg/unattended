# Research: a hex-native electorate layout

Design system: product/nz_election/DESIGN.md (the hex map component reads this snapshot).

## Goal
`product/nz_election/snapshots/hexmap.json` places the 64 general and 7 Maori electorates on a square grid;
`home_graphics.hex_map` draws it with odd rows offset, so the North Island looks ragged. Produce a layout
designed for hexagons: each electorate gets offset coordinates (odd-r, pointy-top) such that neighbours on
the grid are neighbours on the 2025 Stats NZ geometry where possible, Auckland is enlarged as now, the
South Island is one contiguous shape, and the 7 Maori electorates form their own compact cluster to the
right (two columns, north to south).

## Read first
`product/nz_election/runbook.md` (snapshot rules), `snapshots/hexmap.json`, the committed 2025 geometry
named in its `source_url`, `pipeline/home_graphics.py` `hex_map`.

## Output
This job is read-only: put the full file in one fenced json block in your final message (the wrapper saves it to last.md), in the existing hexmap schema with an
added `"layout": "hex-odd-r"` and a `method` sentence; every one of the 71 slugs exactly once; no two
cells on the same coordinates. Report in last.md: a neighbour-agreement count (pairs adjacent on the grid
that are adjacent in the geometry) for old and new layouts.
