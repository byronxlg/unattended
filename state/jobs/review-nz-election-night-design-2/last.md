Verdict: **request changes**

Critical: None found.

Important:

- [night_electorates.py:100](/Users/byron/repos/unattended/.worktrees/nz-election-night-design/product/nz_election/pipeline/night_electorates.py:100): Search now hides provenance guidance. The `.night-map-key` wrapper contains both “Provisional leaders, not elected members” and the original-boundary/no-vote-transfer disclaimer. Existing search handlers hide this entire wrapper when filtering. Previously those caveats stayed visible. Keep them outside the hidden map/key content.
- [test_night_design_followup.py:49](/Users/byron/repos/unattended/.worktrees/nz-election-night-design/product/nz_election/tests/test_night_design_followup.py:49) and [test_night_page.py:242](/Users/byron/repos/unattended/.worktrees/nz-election-night-design/product/nz_election/tests/test_night_page.py:242): New tests pin exact classes, HTML strings, element structure and serialized markup order. This violates the stated test constraint. Further examples occur at followup lines 56-58 and 82-84. Retain data/accessibility assertions; assess layout through browser behavior and screenshots.

Nit: None.

Read-only probes confirmed search precedes majority cards in replay, live, settled and official rendering. Packaged hemicycles retain the correct dot counts, contiguous wedges, non-overlapping dots and matching marker/underlay paths. Timezone uncertainty and EC attribution remain explicit.

The banner-scoped harness retains masthead overflow and 44 px target checks; nested module headers contain no links whose coverage is lost.

**Visual limitation:** Chromium launch failed with sandbox `EPERM` on temporary-directory creation. The ordering defect is structurally resolved, but I could not verify all four states at 390 px by eye. No pytest run; the supplied 452-pass host result does not establish that visual requirement.