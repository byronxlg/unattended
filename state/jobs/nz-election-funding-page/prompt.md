Build: a dedicated funding page (Byron, issue #103: "Let's make a dedicated funding page. That's interesting").
Worktree .worktrees/nz-election-funding-page, branch change/nz-election-funding-page from origin/main. Commit, never push.

Page plan: intent/nz-election/pages/funding.md (questions, answers, graphics, page order; build exactly that order).
Design: product/nz_election/DESIGN.md (tokens and components; reuse them, add no new token; 16 px reading floor from #93).
Read first: AGENTS.md, the page plan, DESIGN.md, pipeline/donations.py and snapshots/donations.json (146 EC returns,
party_id, amount_nzd, received, document_url), pipeline/parties_page.py (its "Who funds it?" block), pipeline/home.py
(how home links pages), pipeline/build.py (route registration), how parties/ was added in PR #61 (git log --grep parties).

Goal: route `funding/` answering the plan's five questions in its order:
1. Headline sentence (party with the largest declared total, amount, count) with the caveat "returns over NZD 20,000,
   not total party funding" and the retrieval date beside it; ranked horizontal bar chart of declared totals by party,
   amount and return count labelled at each bar end, party colours from DESIGN.md.
2. Ten largest donations: donor, party, amount, received date.
3. Cumulative declared total by received date, a step line per party with three or more returns, end labels; parties
   omitted are named in the caption.
4. Full list newest first, grouped by party, each group anchored `#<party_id>`, each row linking its EC document.
5. EC credit and licence line (donations.LICENCE). Rows with document_checked false are listed, never excluded.
Link it from the home feed and from each party's "Who funds it?" block on parties/ (to funding/#<party_id>).
Charts are server-rendered SVG like home_graphics.py; no new JS. Absent data is never rendered as "not available".

Contracts: the route count, route lists, screenshot targets and family sets pinned in existing tests move with the
registered set (this adds a route); nothing weaker. New tests check data, provenance, absence and accessibility (totals
equal the sum of records per party, every row's document link present, every chart has a text equivalent, anchors
resolve), never markup, class names or pixel sizes.

Done when: `uv run --with pytest pytest -q product/nz_election/tests` passes except Chromium launches the sandbox denies
(list them by name), `bin/lint` prints lint ok, and last.md says which pinned contracts moved and why. The supervisor
judges funding/ by eye at 390 and 1280 against the plan's question test.

## Supervisor note, 2026-10-26 20:15Z (design-loop critique)

The masthead nav already wraps to two rows at 390 with seven links (Night and Methods alone on row two, about 160 px
of header). Adding Funding must leave it no worse: pick a link set that fits one or two rows at 360 and 390 with
16 px type and 44 px targets (for example Methods moves to the footer), and show the header at 390 in your
screenshots. Do not shrink type below the floor or let links run off screen; screenshots.py HEADER_OVERFLOW and
HEADER_TARGET_BOUNDS must still pass.
