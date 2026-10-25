Verdict: **request changes**.

**Critical:** None found.

**Important:**

- [web/night-live.mjs:67](/Users/byron/repos/unattended/.worktrees/nz-election-results-states/product/nz_election/web/night-live.mjs:67): Official handover leaves the navigation link labelled **“Live preliminary results”**. It sits outside the replaced snapshot, generated at `pipeline/night_page.py:106`. Removing `#night-result-status` closes the due-date issue but not all obsolete preliminary copy. Update the navigation label and extend the handover assertion.

- [tests/test_contracts.py:19](/Users/byron/repos/unattended/.worktrees/nz-election-results-states/product/nz_election/tests/test_contracts.py:19): A test present on `c2ce1fc` is modified: the capture count changes from 142 to 144. The additional assertion does not weaken coverage, but this violates the explicit requirement that main’s tests remain untouched.

**Nit:** None.

Provenance probes passed: valid official input accepted; preliminary feed with edited dates/label, old XML with official provenance, external source-clock edits, and malformed provenance rejected. Source time is reparsed from XML. Backward transitions were rejected; publication also guards state rank.

Question test: available phone screenshots show National 63 against 62 required in settled state; official shows both parties at 61. Completeness/currentness reads 100%, updated 23:30. Q3 now asserts **CHANG, Johan**, a 5,000-vote margin and visibility within one scroll. Current Q3 screenshots were unavailable locally, so that visual check remains unverified independently.

No pytest or writes. Probes used `.venv/bin/python -B` because `uv` required a cache write blocked by the read-only sandbox.