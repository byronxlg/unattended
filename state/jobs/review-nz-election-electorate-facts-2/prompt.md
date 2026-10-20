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


## Second review

This is the second fresh review of PR #54 after fix-1 (99f69dc: correction values validated by field) and a merge of main (voting snapshot, conflict in snapshots.py NAMES resolved as the union). The first review's finding was:

**Verdict: request changes.**

**Critical:** None found.

**Important:**
- `product/nz_election/pipeline/snapshots.py:161`: Correction values are not validated. In-memory probes confirmed `load('candidate-reconciliation-2026')` accepts `after` values of `""`, `null`, `[]`, `{}`, integers, floats and huge integers for a name correction. Validate `before` and `after` according to `field`, and add rejection tests. This violates the malformed-input requirement.

**Nit:** None.

Checks completed:

- Eight name corrections match the reconciliation’s EC spelling exactly: Sales, Turner, Wellman, Leavasa, Stobo, Arneil, Carter and Stephens. Their spellings also match the [official EC party-list PDF](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf).
- Both affiliation corrections match the recorded EC entries: Kane, row 207; McIntosh, row 231. Both become Independent. Independent verification against the XLSX was blocked by network/content-type restrictions.
- Exactly 60 names and two affiliations changed. No list rank, MP flag or photo changed. All 50 previously omitted ranks remain omitted.
- Boundaries: 71 features, exact registry/hexmap slug coverage, 316,359 bytes. Licence, attribution, source URLs and simplification recorded; explicitly excludes legal-boundary/address-lookup use.
- EC-derived content contains facts and provenance, with no copied source prose found. Join rules and explicit exceptions are recorded; no fuzzy matching found.
- Loaders are offline; all three snapshots load. Existing tests remain untouched, including against `d55b42e`.

Verification limits: `uv run --with pytest pytest -q product` and `bin/lint` both stopped with `Failed to initialize cache … Operation not permitted`. PR-body retrieval also failed. No files changed.

Check that finding is fixed, that no test on main at 6a07d2c was weakened, and review the rest as before. Verdict accept or request changes.
