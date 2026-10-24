Fresh-context review of PR #75 (nz-election-campaign-verify), read-only. Worktree .worktrees/nz-election-campaign-verify,
branch change/nz-election-campaign-verify, head eb27b19. Diff: git diff bec0594...eb27b19 -- product. Judge against REVIEW.md.

Context: adds `verify.py campaign` (pipeline/campaign_checks.py) with named invariant checks over the campaign data
families, wired into `verify.py all`, and test_campaign_verify.py (95 tests). No UI, workflow or data changes. Check:
each check names the invariant and fails with a stable code (no raw data, wikitext or upstream text in messages);
every check would fail on a realistic regression (a test shows each failing), not only on malformed input; nothing
in an existing check is loosened or removed from `all`; checks read only --data and committed snapshots (no network);
`verify.py all` ordering and exit codes unchanged for the other families; it runs in the daily/hourly workflows'
time budget (it passed on the host against the live data branch).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
