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

--- Second pass 2026-10-17 01:10Z (supervisor) ---
This is the second fresh review. The first review (00:37Z) found eight Important and two nits;
the engineer's fix round landed as 0108d71 (git diff bed5452..HEAD is the fix, 73378ab is main).
Judge the whole branch again, but start from the eight: for each say fixed, not fixed, or
fixed with a new defect, with file:line. The decisions the engineer was given: the two test
assertions (test_coalitions.py:149, test_increment_two_regressions.py:184) may return to full
strength and nothing weaker; finding 8 (per-route OG cards) is deferred to the feed home; the
unavailable OG card's empty lower half is deferred. Check that the rewritten strip test is at
least as strong as the 73378ab version it replaced (it must now verify positions, widths,
markers and connectors numerically, not only presence). Check the Node parity cases for the
strip actually compare the client markup with the server markup, not two client renders.

The engineer's reply, verbatim:
Committed `0108d71`. Not pushed; worktree clean.

1. Empty windows render unavailable; new regression and baseline comparison render, and empty-window verification passes.
2. Restored full strip/table equality and numerical position, width, marker, and connector checks.
3. Python/JS strip markup matches exactly, including accessibility, table columns, disclosures, and precision; three Node parity cases cover overhang.
4. Source labels derive per source; original links and licences are visible outside disclosures.
5. Compact provenance prose, wrapping 44 px action rows, and unpadded OG links implemented. Visual review remains pending.
6. Methods link remains visible in both unavailable forms.
7. One pipeline presentation record supplies page and OG availability, headline, selected polls, and provenance.
8. Per-route OG publication and `og:image`: deferred as requested.
9. Focus nit: main is blurred after testing; skip-link and main focus get separate captures.
10. Unavailable OG whitespace: deferred as requested.

Verification tails:

```text
pytest -q product/nz_election/tests
294 passed in 141.04s (0:02:21)

Final targeted design/review tests
24 passed in 22.24s

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS refresh: polls bundle
PASS build: 77 routes
PASS all

bin/lint
lint ok (314 text files)
```

CSS: 11,000 bytes. Built home transfer: 17,858 bytes before reserved font.

Both screenshot commands failed at Chromium launch with sandbox `Permission denied (1100)`. I could not inspect the requested images or verify browser axe results. Host commands:

```sh
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --og-only --out /tmp/ds-og
```
Screenshots attached were taken on the host from 0108d71: home at 360, 390 and 1280, the dark
variant, main-focus and keyboard-focus captures, night at 360 and 1280, Wellington North at 390
and 1280, polls OG card and the Wellington North OG card. Host harness on 0108d71: PASS
screenshots 77 routes 204 images; OG pass 2 images; source_note_bottom 516.78 at 360 and 390.
Same report format as before, last line "Important findings: N".
