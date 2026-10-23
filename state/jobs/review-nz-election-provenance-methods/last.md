The compact source rendering removes freshness and refresh-failure warnings from electorate pages. Verification was limited to code inspection because the read-only sandbox blocked the attempted runtime probe.

Review comment:

- [P2] Preserve refresh warnings in compact electorate footnotes - /Users/byron/repos/unattended/.worktrees/nz-election-provenance-methods/product/nz_election/pipeline/electorate_pages.py:33-35
  When an electorate dataset is stale or its refresh fails, this early return bypasses the status handling below. All electorate detail pages use this compact path, so they now display retained candidate, enrolment and local-poll data without the previous update-failed or overdue warning; the warning appears only after navigating to Methods. Keep operational freshness warnings on the electorate page while relocating detailed provenance.