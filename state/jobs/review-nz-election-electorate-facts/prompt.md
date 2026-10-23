Fresh-context review of nz-election-electorate-facts, read-only. Worktree .worktrees/nz-election-electorate-facts,
branch change/nz-election-electorate-facts, head f28be8e on main. PR body (`gh pr list --head change/nz-election-electorate-facts`)
is a claim to check. Diff: git diff main...f28be8e. Judge against REVIEW.md, the brief
state/jobs/nz-election-electorate-facts/prompt.md (main checkout) and the page plan intent/nz-election/pages/electorate.md.

Check: (1) spot-check at least eight of the 60 name corrections and both affiliation changes against the EC
reconciliation records (evidence recorded, EC spelling verbatim, no fuzzy join); (2) no list rank, MP flag or
photo changed; (3) boundaries: 71 features, slugs match config/electorates.json and snapshots/hexmap.json exactly,
licence and attribution recorded, file under 400,000 bytes, no geometry claimed as legal boundary; (4) EC data has
no open licence: is what is stored limited to facts (names, parties, ranks) with provenance, no copied prose;
(5) loaders and tests are offline and fail on malformed input; (6) no test on main weakened; (7) nothing invented
to fill a gap (the 50 omitted ranks stay omitted).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
