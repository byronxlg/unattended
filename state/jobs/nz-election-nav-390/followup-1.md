# nz-election-nav-390 fix-1

Host run on 3304028 (Chromium on the host, where your sandbox cannot launch it):
`uv run --with pytest --with playwright pytest -q product/nz_election/tests -k "design or home or nav or header"`
gave 1 failed, 165 passed: `test_design.py::test_phone_rendered_type_and_targets[header]`,
type_scale_browser.py -> screenshots.py:155 header_check, `HEADER_TARGET_BOUNDS`.

Supervisor diagnosis on a live-data build of 3304028, home at 360 and 390, each banner link focused in order:
the nav clip is 16..324 (360) and 16..354 (390); "Electorates" when focused sits at 289..389, so it is
partly hidden under the clip edge and the cue. Chromium does not scroll a partly visible focused element
into view, so a keyboard user sees a half-clipped focus ring. Vote and Night are fine once reached (the
container scrolls for them). The check is right; the header is wrong.

Do:
1. Make every focused header link fully visible inside the nav at 360 and 390 when reached by Tab
   (for example scroll-padding-inline on the nav plus a focus scroll, or a small handler that calls
   scrollIntoView({block:'nearest', inline:'nearest'}) on focusin; if you add a script, register it the
   way the existing page scripts are registered and validated, and the header must still work without it
   for mouse and touch). Keep one row, 16 px text, 44 px targets, the visible cue, no page overflow.
2. Do not weaken header_check or any test. The branch's own header_check is correct as written.
3. Commit. Say in last.md exactly what you changed and that Chromium tests need the host run.

Done when: the same pytest command passes on the host (supervisor runs it), `bin/lint` prints lint ok.
