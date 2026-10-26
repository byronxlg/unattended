# Design backlog

Newest first. The supervisor adds the three weakest things on the site once a day ("Design loop" in
`prompts/supervisor.md`) and Byron's design feedback verbatim; the top item is the next UI change.

## 2026-10-26 (redesign, Claude)

1. Electorate pages (`electorates/<slug>/`) still use the pre-redesign layout: bring them onto
   DESIGN.md (hero with holder and margin, candidate cards with photos, the hex map with the seat
   highlighted).
2. Parties, vote and night pages: same, page anatomy and components from DESIGN.md.
3. Hex map shape: the square-tile snapshot drawn with offset rows looks ragged in the north; a
   hex-native layout (`snapshots/hexmap.json` with axial coordinates) would read as New Zealand.
