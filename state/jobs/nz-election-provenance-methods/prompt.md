# nz-election-provenance-methods: move per-record source dumps to anchored Methods sections

Goal: design-principles.md rule 5 on the routes PR #37 opened up. Today electorate pages and
polls/ render every individual source record (name and party locators per candidate, every poll's
source record) in open disclosures next to the content. At 360 px the electorate locators push
the second candidate below the fold. Move the detailed records to anchored sections on the
Methods (or sources) page; leave one compact grey footnote line per module naming the source,
the licence/attribution and the update time, linking to that module's anchor. Nothing is deleted;
it moves (rule 5: full provenance reachable in one click).

Read first: intent/nz-election/design-principles.md (rules 4, 5), the PR #37 fresh review
(state/jobs/review-nz-election-principles-routes/last.md), product/nz_election/pipeline/
electorate_pages.py near line 66, build.py near line 371, the existing Methods/sources route,
and the disclosure and fragment checks in product/nz_election/tests/ (screenshots.py, the
disclosures and local-fragment checks).

## Constraints

- Every existing fragment id that pointed at a source record still resolves (keep the id on the
  new Methods anchor or leave a redirecting anchor); the local-fragment check must stay green
  with no ids removed from its baseline.
- Attribution and licence text required by a source stays adjacent to the figure it covers.
- Raw locators (wikitext, revision locators) are not reader text on electorate pages; on Methods
  they are presented as records, not dumps. No raw posts, handles or keys anywhere.
- Harness checks that must still pass and must not be loosened: disclosures, AXE landmark-unique,
  SOURCE_NOTE_BELOW_FOLD, PAGE_OVERFLOW, SMALL_TARGET, MISSING_SOURCE, market budgets, home
  byte budget and measure_home. Home is out of scope; leave its HTML unchanged if you can, and
  say so in last.md either way.
- Tests on main at the base sha are protected except assertions that pin the open-dump markup
  this change moves; name each one you move and why. Your branch's own tests move with it.
  Nothing weaker. No new data source.

## Done

- `uv run --with pytest pytest -q product/nz_election` passes; `verify all` PASS; `bin/lint` ok.
- A no-Chromium check over the built HTML that fails on the base sha and passes on HEAD: on an
  electorate page and on polls/, no element outside the footnote carries per-record source
  locators, and each footnote links to a Methods anchor that exists and holds the records.
- Commit in the worktree, never commit last.md, do not push. last.md: what moved where, the
  fragment ids kept, the tests moved and why. The supervisor runs the Chromium harness and looks
  at an electorate page and polls/ at 360 and 1280, and Methods at 1280.
