**Verdict: request changes.**

**Critical:** None found.

**Important:**

- [vote_page.py:86](product/nz_election/pipeline/vote_page.py#L86): Enrolment is marked “already shown” whenever its date exists. From midnight on 26 October, the enrolment answer only says “The enrolment close has passed”; the timeline retains the date but omits midnight. Skipping the help deadline therefore removes source precision that the parent branch displayed. Preserve the exact deadline once in the closed state, and test that visible content across phases.
- [vote_page.py:108](product/nz_election/pipeline/vote_page.py#L108): Deduplication covers only help entries. Domestic voting’s 7pm deadline still appears in the timeline and help, plus the countdown on election day. This misses the brief’s “each deadline said once” requirement.
- [vote_page.py:126](product/nz_election/pipeline/vote_page.py#L126): Missing `retrieved_at` raises `KeyError`. Removing it from any snapshot record crashes rendering. This limitation also exists in the parent’s date/global credits, so it is **pre-existing**, but the requested sparse-record check fails and the new help credit repeats the assumption.

**Nit:** None.

Python probes, without pytest:
- All four hard-coded phrases match snapshot summaries, dates and `at` times.
- 1,055 empty/single/pair-record renders across five phases: all description IDs resolve.
- Individually missing `at`, `date`, or `source_url`: no crashes or dangling references.
- Added tests check provenance and action absence, but miss deadline precision and repetition.

Read-only; no changes. The brief file was absent from this worktree, so I used your supplied requirements. Desktop CSS gives labels and answers the same column; screenshots were not independently inspected.