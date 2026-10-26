# Build: type scale and the party funding headline (issue #92)

Byron (Telegram 2026-10-26 02:35Z, verbatim): "It's better. I feel like there is a lot of small
text. And the party funding total is hidden in a paragraph which I feel should be promoted"

Design system: product/nz_election/DESIGN.md (tokens and components; it sets how things look).
Page plan: intent/nz-election/pages/parties.md (it sets what the parties page answers and in what order).

Read first: product/nz_election/DESIGN.md, product/nz_election/web/styles.css (and any other
web/*.css), product/nz_election/pipeline/parties_page.py around the "Who funds it?" block (about
line 140), intent/nz-election/pages/parties.md, REVIEW.md pass 4.

## 1. Too much small text (site-wide)

The CSS declares font-size about 160 times; most reading text sits at 13 to 14 px against a handful
at 16 px. Set a type scale as tokens in `:root` (for example --fs-caption, --fs-small, --fs-body,
--fs-lead, --fs-h3, --fs-h2, --fs-h1, --fs-figure) and use them instead of literal sizes.
Reading text (paragraphs, list items, table cells, card bodies, nav, buttons, links in prose) is
16 px or more on phone and desktop. Below 16 px is only for: captions and source credits
(.source-note, .party-credit and similar foot lines), chart axis ticks and labels, and small
labels on dense tables; those stay at 13 px or more. Chart `<text>` rule in DESIGN.md still holds
(never below 12 px on a 360 px phone). Add the type scale to DESIGN.md's Tokens section in two or
three lines.

## 2. Party funding total as a headline figure (parties page)

In each party's "Who funds it?" block, the year's declared total becomes a large figure at the top
(the figure style DESIGN.md uses for headline numbers, tabular), with the count of declared returns
beneath it in one short line, then the largest donors list. The caveat "not total party funding"
sits next to the figure (one short line under it), not only in the credit line. Keep the
data-total and data-count attributes and the source link. If it reads well, add one small
cross-party comparison near the top of the parties page: each party's declared total this year as
a horizontal bar in its party token colour, sorted, with the figure labelled, the same caveat and
the EC source link; drop it (render nothing) when no party has donations.

## Constraints

- Presentation and markup only; no data or pipeline changes beyond reading the donations rows the
  page already reads.
- Tests check data, provenance, absence and accessibility, never markup, class names or byte
  counts. Existing tests on main that pin a font size, a class name or the old sentence wording may
  move with this change; say which and why in last.md. Do not weaken any data, provenance, absence
  or accessibility check.
- No horizontal scroll at 360 px; no "not available" text; dark mode works (tokens only).
- Commit in the worktree; do not push.

## Definition of done

- `uv run --with pytest pytest -q product/nz_election/tests` passes (Chromium tests may skip in
  your sandbox; say which skipped).
- `bin/lint` prints ok.
- Build the site and take screenshots of home, polls/, parties/, vote/ and one electorate page at
  390 and 1280 (`uv run --with playwright python product/nz_election/tests/screenshots.py` or
  Playwright directly); put the paths in last.md and write the three weakest things you see.
- last.md lists: the type tokens and their values, any test that moved and why, and
  `rg -c "font-size" product/nz_election/web/*.css` before and after.
