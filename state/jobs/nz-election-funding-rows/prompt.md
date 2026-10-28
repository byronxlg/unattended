# Build: funding/ returns readable at 390 without sideways scroll

Page plan: intent/nz-election/pages/funding.md
Design: product/nz_election/DESIGN.md (tokens and components; use them, add none unless DESIGN.md is updated in the same change)

## Goal
On funding/ at 390 px each party's returns table is `min-width:620px` (product/nz_election/web/styles.css:541), so a reader has to scroll sideways to compare donor, amount and date. Design backlog 27 Oct 08:30Z (state/design-backlog.md). At phone widths, show each return so donor, amount, date and the source document link read together inside the column with no horizontal scroll; at 1280 the table stays as it is.

## Read first
- product/nz_election/pipeline/funding_page.py (markup of the returns)
- product/nz_election/web/styles.css lines 526-560
- intent/nz-election/pages/funding.md, DESIGN.md
- REVIEW.md pass 4

## Constraints
- Every return and its source link stays on the page (data unchanged); no figure is dropped at any width.
- Keep the table semantics for screen readers (a real table, or a list with equivalent labels; your choice), accessible names for every amount.
- Tests check data, absence and accessibility, never markup, class names or byte counts. Existing tests on main at the base sha are not edited unless the registered contract moves with this change; say which if so.
- Commit in the worktree; do not push.

## Definition of done
1. `uv run --with pytest pytest -q product/nz_election/tests -k 'funding or design'` passes (host runs it with Chromium too).
2. A new browser check: funding/ at 390 and 360 has document scrollWidth equal to the viewport width and every returns region has scrollWidth <= clientWidth; it fails on origin/main and passes on HEAD. Say the command and both results.
3. `bin/lint` ok.
4. Report in last.md: files changed, the commands and their output lines.
