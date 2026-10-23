# nz-election-parties-refine: two deferred PR #61 items

Page plan: intent/nz-election/pages/parties.md (accepted). This is a refinement round on the live parties/ page; it changes no page order and adds no content.

Worktree `.worktrees/nz-election-parties-refine`, branch `change/nz-election-parties-refine` from main. Read first: `AGENTS.md`, `REVIEW.md`, the third fresh review of PR #61 (`state/jobs/review-nz-election-parties-page-3/last.md` in the main checkout, summarised below), `product/nz_election/pipeline/snapshots.py` around line 450, the parties page template and the credit caption code it uses.

## Items

1. Licence validated per source, not against the global set. Today `snapshots.py:450` accepts any recognised licence, so `CC0` or `Public domain` passes on the two snapshot types whose provenance is EC copyright and Policy.nz link-only. Enforce the licence each source type actually carries (find where host and path are already pinned per type and put the licence beside them). Tests: a recognised-but-wrong licence is rejected for each of those types; a missing `source_url` is rejected. Show both tests failing on the base sha.
2. Credit captions on parties/ render a stray "/" before the licence and a leading ". " when an author or source field is empty (empty parts joined). Join only non-empty parts. Test on rendered HTML: no caption on parties/ starts with ". " or contains " / " followed by nothing or preceded by nothing.

## Constraints

- Committed snapshot records stay valid (they are correct today); if one fails the new check, stop and say which.
- Tests on main at the base sha are protected except where an assertion pins the buggy caption string; if one does, change only that assertion and say so. This branch's own tests move freely.
- No threshold in `screenshots.py`, `home_checks.py` or `market_checks.py` changes.
- Commit in the worktree, do not push, do not commit `last.md` or `artifacts/`.

## Done

- `uv run --with pytest pytest -q product/nz_election/tests` passes (state the count), the new tests fail on the base sha (state the command and output).
- `bin/lint` prints `lint ok`.
- `PYTHONPATH=. uv run python -m product.nz_election.pipeline verify all` (or the repo's documented equivalent) PASS.
- Chromium does not start in your sandbox; the supervisor runs the screenshot harness on the host. Say what to look at.
