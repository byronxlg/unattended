# Build: campaign/ reads as retained advance-voting history after voting closes

Page plan: none for campaign/ (copy only). Look: product/nz_election/DESIGN.md. No layout change.

## Goal

After voting closes (7 Nov 06:00Z, `pipeline/sunsets.py` `post_election`), campaign/ still says
"What is happening in the campaign?" (`pipeline/build.py:573`) and "How many people have voted
early?", "running total" (`pipeline/campaign_page.py:69`); its `built` argument never changes the
copy. A reader on 10 Nov should read past tense: the 2026 advance votes as retained observations,
dated, with the source note unchanged.

## Invariants

- The switch uses `post_election(built)` from sunsets.py; no literal timestamps.
- Before the close, output is byte-identical to today.
- After the close: heading and module question past tense (e.g. "What happened in the campaign?",
  "How many people voted early?"), the chart caption and lede say the counts are the 2026 advance
  votes observed through the last date; numbers, table, provenance and source note unchanged.
- Empty state (no advance rows) after the close says so in past tense, no placeholder.

## Read first

`pipeline/campaign_page.py`, `pipeline/build.py` 560-580 (how vote/ and electorates switch with
`post_election`), `pipeline/sunsets.py`, `tests/test_sunsets.py`, campaign tests (`rg -l campaign product/nz_election/tests`).

## Tests

Renderer assertions on data and wording (not markup or class names) at 6 Nov 12:00Z, 7 Nov 06:00Z,
7 Nov 10:00Z, 14 Nov 00:00Z, 27 Nov 00:00Z, populated and empty. Tests on main at the base sha are
protected except an assertion pinning the present-tense wording after the close: that contract
moves; name it in last.md. New cases must fail on origin/main's code.

## Done

`uv run --with pytest pytest -q product/nz_election/tests/test_sunsets.py` plus every campaign test file, 0 failed;
`bin/lint` ok. Commit in the worktree; do not push. last.md: files, moved contract, cases failing on base.
