Fresh-context review of PR #93 (nz-election-type-scale), read-only. Worktree .worktrees/nz-election-type-scale,
branch change/nz-election-type-scale, head 679e2fc on main 01b25d7. Diff: git diff origin/main...679e2fc.
Judge against REVIEW.md, including pass 4 against intent/nz-election/pages/parties.md and product/nz_election/DESIGN.md.

The change (Byron, issue #92: "a lot of small text; promote the party funding total out of its paragraph"): type
tokens in web/styles.css with a 16 px floor for reading text; every font-size in the five CSS files uses a token or
inherits; parties/ shows the donations total as a headline figure with its caveat. Check: no reading text (sentences,
answers, list items, table cells a reader reads) is left on --fs-caption or a smaller literal; caption is only on
credits, source lines, chart notes and dense labels; nothing overflows horizontally at 360 from the larger sizes
(long tokens, tables, chips, nav); SVG text scaling stays readable; the funding figure keeps provenance (EC link,
the "not total party funding" caveat adjacent, the 20,000 threshold before the total as the campaign checks want);
the three moved test assertions pinned literal px values only and nothing that checked data, provenance or
accessibility was removed. Supervisor host run: origin/data build PASS build: 81 routes; screenshots of home,
polls, parties, vote, electorates/wellington-bays at 390 and 1280 at /tmp/ts/shots/*.png (read them). Do not run
pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
