**Verdict: request changes.**

**Critical**
- None found.

**Important**
- [styles.css:9](product/nz_election/web/styles.css:9): The 390×844 question test fails for question 2. Only its heading fits; the actual poll-change answer is below the fold. Screenshot answers: Q1 “Governing parties: 67 seats, 3 more than the 64 needed”; Q2 unreadable; Q3 “Enrol by 25 October; advance voting from 26 October; election day 7 November.” Dates and “How to vote” fit.
- [styles.css:9](product/nz_election/web/styles.css:9): Keeping the map and list in equal columns on mobile shrinks electorate targets to approximately **9×9 px**. The primary picker is difficult to tap or identify visually. Native links and focus styling remain, but the target-size harness explicitly excludes SVG links.
- [test_home_defects.py:73](product/nz_election/tests/test_home_defects.py:73): The market proposition test now exercises `market_graphic(envs)`, which the moved module does not render. Methods uses `market_panel.panel`. This check should follow the rendered destination; testing the unused helper weakens its production coverage.

**Nit**
- [home.py:372](product/nz_election/pipeline/home.py:372): Confirmed duplicate directory links: “Browse all electorates and candidates” and “See all electorates.”
- [snapshot_views.py:105](product/nz_election/pipeline/snapshot_views.py:105): Refute the supervisor’s interpretation of the loose hex markers: these are the seven Māori electorates, not closest-margin row markers. Confirm the visual ambiguity; label that column directly.

Boundary probes passed at both specified UTC instants. Historical/demo-only data did not trigger handover. Seat totals, majority and overhang are computed; deltas compare consecutive descriptive averages using their respective scales. Shading says “poll range.” Markets retain provenance and terms.

Read-only checks returned `home_checks PASS; ABSENT_TEXT 81` for before/after/night, provenance passed, and inbound-home-fragment scan returned `[]`. Host logs report `1925 passed`; both screenshot-harness logs end with `AssertionError: SMALL_TARGET`, so browser verification remains incomplete.

PR-body claims could not be checked: `gh` could not connect; the GitHub connector requires reauthentication. No files changed.