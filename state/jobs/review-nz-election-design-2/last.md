- **Important:** `product/nz_election/pipeline/build.py:290,300` passes average and seat envelopes to `source_note`, whose fieldwork extraction only understands poll rows (`:100`). Both notes therefore show retrieval time without the underlying fieldwork date. `web/templates/source-note.html:2` also describes both as “Seats calculated by this site,” including when seats are unavailable. Supply the contributing polls and calculation-specific wording. Add assertions for each note’s dates and meaning; existing provenance tests check references, not their accuracy.

Prior eight findings, in order:

1. **Fixed:** `pipeline/build.py:143-156` withholds an empty-window result; `tests/test_design_review.py:26` checks rendering, retained history and visible methods.
2. **Fixed:** `tests/test_coalitions.py:151` restores complete strip/table equality. `tests/test_increment_two_regressions.py:198-225` numerically checks positions, widths, rows, connectors and majority marker. The replacement retains the old test’s spatial intent under the new grammar; no remaining weakened existing assertion identified.
3. **Fixed:** `tests/test_design_review.py:14-23` compares Node markup directly with Python markup. Independent execution passed overhang 0, 2 and 17, including accessibility attributes, disclosures and table columns.
4. **Fixed:** `pipeline/electorate_pages.py:10-38` derives publishers per source and exposes original links and licences outside disclosures.
5. **Fixed:** `web/styles.css:26` separates compact prose from wrapping 44 px action rows and removes padding on OG links. The former inflated line boxes should have blocked; the current screenshots resolve them.
6. **Fixed:** `pipeline/build.py:254,275` keeps the methods link visible in both unavailable forms.
7. **Fixed:** `pipeline/build.py:439-440` and `tests/screenshots.py:237-241` share the presentation record for availability, headline, selected polls and provenance.
8. **Not fixed, explicitly deferred:** `web/templates/base.html:3-11` still has no `og:image`; `tests/screenshots.py:234` generates only two review cards. No renewed blocker under the supervisor’s decision.

`tests/screenshots.py:101` fixes focus contamination by blurring main before baseline captures; separate captures preserve keyboard testing. Keep the real focus behaviour. OG uses fresh content and is not tainted.

Budgets are measured from built files, not claimed constants (`tests/design_checks.py:32`, `tests/test_design.py:99`). Independently measured: CSS **11,000 bytes**; existing host home **17,859 compressed bytes**, **62,859 with font reserve**. The new suite would fail on `73378ab`, including absent presentation functions and tokens; not every individual check distinguishes main. No baseline execution claimed.

Axe is **553,446 bytes**, includes MPL-2.0 licence and copyright notice, and matches the recorded SHA-256. Build copying excludes it; no axe files exist in the inspected host output. No source-data, route-configuration or workflow changes found. Availability behaviour does change intentionally, and the build adds `home-presentation.json`. No additional security finding.

Full pytest rerun was blocked: `uv run --offline --with pytest pytest ...` returned `Failed to initialize cache ... Operation not permitted`. Browser results remain the supplied host evidence.

The screenshots **pass the five-second test for the unavailable form**: election identity, absence of a seat estimate, poll date and attribution are visible before scrolling. Light and dark layouts remain legible. Current desktop and OG provenance wraps normally without inflated gaps. First change: correct the provenance wording and dates above, especially the claim of calculated seats beneath an unavailable headline. The unavailable OG’s empty lower half is visually weak but remains a follow-up, as explicitly deferred. These images cannot establish the available-seat form’s visual quality.

Important findings: 1