# Follow-up 2: nz-election-advance-2026 (fix round, PR #114)

The fresh review found one Important item, confirmed by the supervisor:

- `product/nz_election/pipeline/vote_page.py:71` `advance_line()` omits `source['provenance']`. The
  count is a hand transcription of the EC voting statistics page; home and vote/ show the number, the
  source URL, retrieval time and caveat, but never say it was transcribed by hand. Add a short
  disclosure beside the number on both pages (plain words, e.g. "transcribed from the EC page"),
  drawn from the capture's provenance field, not a literal. If provenance is absent, the line still
  renders without the disclosure (no "not available" text).

Tests: add assertions that the disclosure appears in both rendered pages for a hand-transcribed
capture. Tests on main at the PR base are protected; tests this branch added may move with it.
Do not pin markup or class names; assert visible text.

Read first: AGENTS.md, product/nz_election/DESIGN.md, intent/nz-election/pages/vote.md.

Done when committed (not pushed) and:
  uv run --with pytest pytest -q product/nz_election/tests -k "advance or vote or home"   -> all pass
  (Chromium sandbox denials may be listed separately) and bin/lint -> lint ok.
