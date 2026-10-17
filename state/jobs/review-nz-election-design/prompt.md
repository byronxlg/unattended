Fresh-context review of the design-system change, read-only. Worktree
.worktrees/nz-election-design, branch change/nz-election-design, commits on top of main
(git diff main...HEAD; 31 files, all under product/nz_election/). Judge it against REVIEW.md,
all passes including the design pass, and against intent/nz-election/design.md draft 2 (the
accepted design: home sentence in four forms, one label row stripped, source note grammar,
twelve states, budgets: CSS under 12,000 bytes, home first view under 100,000 bytes with a
font reserve, source-note bottom under 780 px at 360 and 390, contrast, axe clean, favicon,
OG template, manifest, night tokens). The engineer's own account is
product/nz_election/DESIGN_REPORT.md: treat it as a claim list to check, not as evidence.

Screenshots attached (--image) were taken on the host from the built fixture site: home at 360
and 390 and 1280, the night variant, one electorate page, the polls page, the OG card. Judge
them on the five-second test in design.md: can a reader on a phone tell what the site is, what
the number is, and where it came from before scrolling. Say what you would change first.

Check specifically: (1) every modified or renamed assertion in the tests: does any existing
check get weaker (the diff lists them; the report says one strip test was renamed); (2) the
new tests in test_design.py and design_checks.py: would they fail on main at 73378ab, and are
the budgets measured or asserted from constants; (3) the seats strip: server render in
build.py and client re-render in coalitions.mjs must stay identical in markup and
accessibility, including the overhang segment after the axe fix on this branch; (4) the
vendored axe-core under tests (licence, checksum, size) and whether it is excluded from the
site output; (5) the screenshot harness tests/screenshots.py activates the skip link and then
captures with main carrying a 3 px focus-visible outline: is that a harness artifact to fix or
behaviour to keep, and does it taint the OG capture; (6) at 1280 the source-note paragraph's
inline links carry a 44 px min-height so line boxes inflate and the retrieval date splits
from "Retrieved" across a wide gap: design defect or acceptable; (7) anything else in
REVIEW.md, in particular anything that would change the live site's data, routes or workflows
(the change claims none).

Report: findings labelled Important or Nit with file:line, then one paragraph on the
screenshots, then a last line "Important findings: N". No emojis, no em dashes.

Addendum 2026-10-17 (supervisor, after the host harness passed on bed5452, four fix rounds in):
the home screenshots attached are the polls-only fixture (no seat estimate), so judge the
unavailable form of the home sentence. Two observations to weigh, not conclusions: (1) the
source note's inline links carry the 44 px tap-target line boxes, so the note is triple-spaced
at 360, 390 and 1280 and on the OG card, where "Retrieved" is split from its date and
"Downloads." sits alone on a line; on a static card that padding looks like a defect to me.
(2) the OG card is blank below the note. Say whether each should block the merge or go to a
follow-up, and what you would do about the line boxes without losing the tap target.
