Fresh-context review of nz-election-donations-facts, read-only. Worktree .worktrees/nz-election-donations-facts,
branch change/nz-election-donations-facts, head b065f31 on main. PR #55 body (`gh pr view 55`) is a claim to check.
Diff: git diff main...b065f31. Judge against REVIEW.md and the brief state/jobs/nz-election-donations-facts/prompt.md
plus its follow-up state/jobs/nz-election-donations-facts-fix-1/prompt.md (main checkout).

Check: (1) every row of the EC donations-exceeding-20000 index for 2026 is present (146), none dropped or duplicated,
amended returns linked to originals; spot-check at least ten records (party, donor, amount, dates, URL) against the
EC page if the network allows, else against the snapshot's own source_locator; (2) party_id mapping agrees with
config/party-map.json; nzof and tttp justified, TOP names both opp; (3) document_checked false is honest and never
used to exclude; (4) the Alajamber exception is pinned narrowly and the loader rejects altered or unrelated
exceptions; (5) stored content is facts with provenance, no copied prose or PDFs; (6) loader and tests are offline
and fail on malformed input, count mismatch, unknown party_id; (7) no test on main weakened; (8) nothing invented
to fill a gap.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
