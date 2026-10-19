# Build: principle 4 on every route (nz-election-principles-routes)

Goal: `intent/nz-election/design-principles.md` principle 4 says routes other than the home may use
`<details>` only for long tables (all polls, all electorates, other long data tables). PR #36 made the
home comply; the other routes still hide prose behind disclosures. Render those openly.

Read first: `intent/nz-election/design-principles.md` (all of it), `REVIEW.md`, `AGENTS.md`, then the
`<details>` emitters: `pipeline/build.py` (89-111 source-actions rewrite into "Sources, inputs and
method", 316 "Why seats are unavailable", 374, 445 manifest record), `pipeline/electorate_pages.py`
(38, 51, 66, 92), `pipeline/home.py:268`, `pipeline/market_panel.py:72`, `pipeline/social_page.py`
(65, 103), `pipeline/route_cards.py:61` (splits on `details class="seat-data"`).

Do:
- A disclosure whose body is prose, a source list, a method note or a short record becomes an open
  section: a small heading (h3 or a labelled `p`) and the content, same ids so every existing fragment
  still resolves. A disclosure whose body is a long table (more than about 12 rows, or the full
  polls, electorates, candidate, party-count or manifest tables) may stay.
- Keep the source-note contract (MISSING_SOURCE, aria-describedby, `p.source-actions` targets) intact.
- Add a check (test plus a harness or verify assertion) that fails when a non-home route has a
  `<details>` whose content holds no `<table>`; show it failing on c6d8ff3 in last.md.
- Tests on main at c6d8ff3 that pin a disclosure's markup move with this change (the registered set
  moved); nothing weaker: every content assertion keeps asserting the same text.

Constraints: no new routes, no colour or layout changes beyond the opened sections; no emojis, no em
dashes; commit in the worktree, do not push; last.md is not committed.

Done when, from the worktree:
- `uv run --with pytest pytest -q product` passes;
- `uv run python -m product.nz_election.pipeline.verify all` prints PASS all;
- `bin/lint` ok;
- the new check fails on c6d8ff3 and passes on HEAD (commands and output in last.md);
- `grep -c '<details' ` on the built methods, polls and one electorate page reported in last.md,
  with each remaining disclosure named and its table row count.
