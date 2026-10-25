Page plan: intent/nz-election/pages/parties.md

Goal: finish the parties page's second-ranked answer. The plan promises each party's verified list size and top five
list candidates; product/nz_election/pipeline/parties_page.py:114 renders opening ranks only, snapshots/
party-list-tops.json:4 disclaims totals, and :180 holds a single Te Pati Maori candidate.

Read first: intent/nz-election/pages/parties.md (answer 2, data, not shown), snapshots/party-list-tops.json and its
validator (grep party-list-tops under product/nz_election), parties_page.py, tests/test_parties*.py, AGENTS.md.
PR #86 (open) also edits product/nz_election/pipeline/snapshots.py for policy-links; keep your validator change local
to the party-list-tops section so a rebase is trivial.

Do:
1. From the Electoral Commission's published 2026 party lists (fetch the real pages or files; never construct a URL
   you did not fetch), record per registered party: list size as published, ranks 1 to 5 with names as the EC prints
   them (title-cased display name kept separate if the source is uppercase), source_url, retrieved_at, and a
   completeness field. A party whose list you cannot confirm keeps what is confirmed and says so in the record; list it
   in last.md. Nothing inferred.
2. Validator: rejects a total without a source, ranks beyond the recorded total, duplicate ranks, non-EC hosts for
   list records. Nothing weaker for existing records.
3. Render: the party picker shows list size and top five where confirmed; an unconfirmed field renders nothing (the
   absent-text gate applies, no "not available").
4. Tests that fail on main for 2 and 3. Pre-existing tests on main at the base sha that pin the opening-ranks-only
   copy may move; name each in last.md.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests/test_parties*.py product/nz_election/tests/test_snapshots*.py` passes.
- `python3 product/nz_election/pipeline/verify.py campaign` PASS; `bin/lint` ok.
- Screenshots of parties/ at 390 and 1280 under the worktree's artifacts/ (untracked); in last.md, the question test:
  what a reader at 390 sees above the fold for the plan's top three questions.
- One commit on change/nz-election-party-lists; do not push; do not commit last.md or artifacts/.
