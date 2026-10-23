Data half of the electorate page plan (intent/nz-election/pages/electorate.md, draft; read its Data section).
No page, route, rendering or client code: snapshots, loader and tests only. Work in this worktree, commit, never push.

Goal, two fetch-once snapshots in product/nz_election/snapshots/:
1. Candidate reconciliation: compare snapshots/candidates-2026.json against the Electoral Commission's official
   2026 electorate candidate and party list release (elections.nz or vote.nz). Record per electorate: matched,
   added by the EC, absent from the EC release, with the EC source URL and retrieval time. Correct
   candidates-2026.json only where the EC release differs, and record each correction. If the EC release is not
   yet published, say so and change nothing.
2. Electorate boundaries: Stats NZ general and Maori electorate boundaries 2025 (CC BY 4.0), simplified for a
   locator graphic, as snapshots/boundaries-2025.json (GeoJSON or TopoJSON, under 400 KB, coordinates rounded,
   names and ids matching snapshots/hexmap.json; list any mismatches rather than fuzzy-joining). Licence, source
   URL, retrieval time and the simplification method recorded in the file.

Read first: AGENTS.md, pipeline/snapshots.py and its tests (the loader pattern used for the existing
snapshots, including the voting.json validation on PR #53 if useful), snapshots/hexmap.json, snapshots/candidates-2026.json.

Constraints: nothing invented to fill a gap (no inferred candidates, no secondary-source substitution for the EC
list); tests offline; existing tests on main at d55b42e untouched, new tests for the loader's rejection of a
missing source, bad licence, unknown electorate id and oversize file. If the Stats NZ download needs an account or
key, stop and say so; do not substitute another boundary source without naming it in the report.

Done: `uv run --with pytest pytest -q product` passes; `bin/lint` prints lint ok; report in last.md (not
committed): sources, counts, mismatches, omissions, file sizes.
