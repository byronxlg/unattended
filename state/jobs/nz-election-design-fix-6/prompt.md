Sixth follow-up on change/nz-election-design, after the second fresh-context review of PR #21
on your 0108d71 (CI green, host harness PASS 77 routes, 204 images). It marks seven of the
eight prior findings fixed and the eighth deferred as decided. One new Important finding
remains; its full text is at the end. This round is that finding only. Reply with the commit
hash, the verification tails, and one line on what you changed. Commit on the branch, do not
push.

The finding, and the invariant it protects:

- Every source note on a page states only what is true of the thing it sits under. Enforced
  nowhere today: the provenance tests check that references exist, not that the sentence is
  accurate. On 0108d71 web/templates/source-note.html says "Seats calculated by this site" in
  every note, including the poll table note, the averages note, the 2023 validation note, and
  the threshold note beneath a headline that withholds seats. On main the sentence was "Parsed
  and averaged by this project", which was true everywhere. This PR must not ship a provenance
  line that is false for the note it sits in.
- Each note's dates describe the data contributing to that note. source_note (build.py:100)
  reads fieldwork_end only from poll rows, so the averages and seats notes (build.py:290, 300)
  show a retrieval time without the fieldwork of the polls they were computed from.

Fix both, your choice of shape. Read first: web/templates/source-note.html, build.py:75-115 and
the three source_note call sites, electorate_pages.py (it may share the template), the
provenance tests under tests/. A reasonable shape: the calculation sentence becomes a per-call
parameter (parsed; averaged with equal weight; seats calculated; seats withheld, see the
headline) and the averages and seats calls receive the contributing polls (average['poll_ids']
against the poll rows) so "Fieldwork ended" is the latest fieldwork among them. The validation
note says what it is. Do not change the visual design, the action row or the OG card.

Tests: add assertions per note for its dates and its sentence (polls, averages, seats available,
seats withheld), in a new test or in test_design_review.py. No existing assertion becomes
weaker; no existing test is edited.

Done means: pytest green; refresh/build/verify; python product/nz_election/tests/screenshots.py
--out /tmp/ds-shots and --og-only --out /tmp/ds-og pass including axe (list any check the
sandbox cannot run as a claim and I will run it on the host); bin/lint clean; one line for the
reviewer: the exact sentence each of the four note kinds now carries.

--- Second fresh review of PR #21 (review-nz-election-design-2, read-only on 0108d71, 2026-10-17 01:07Z), new finding ---
- **Important:** `product/nz_election/pipeline/build.py:290,300` passes average and seat envelopes to `source_note`, whose fieldwork extraction only understands poll rows (`:100`). Both notes therefore show retrieval time without the underlying fieldwork date. `web/templates/source-note.html:2` also describes both as “Seats calculated by this site,” including when seats are unavailable. Supply the contributing polls and calculation-specific wording. Add assertions for each note’s dates and meaning; existing provenance tests check references, not their accuracy.

