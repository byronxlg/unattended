Second fresh-context review of PR #75 (nz-election-campaign-verify), read-only. Worktree .worktrees/nz-election-campaign-verify,
branch change/nz-election-campaign-verify, head 7f027fb. Diff: git diff bec0594...7f027fb -- product. Judge against REVIEW.md.

Context: adds `verify.py campaign` (pipeline/campaign_checks.py) with named invariant checks over the campaign data
families, wired into `verify.py all`. The first review asked for one Important: failure messages forwarded upstream text
(campaign_checks.py:42, 58, 94, 152, 168, 183). fix-1 (7f027fb) emits only owned codes and fixed descriptions and adds
sentinel marker-leak regressions. Check: no failure path anywhere in campaign_checks.py or the verify.py wiring can put
data, wikitext, names or upstream text into a message, log line or exit text; the regressions would fail on eb27b19;
nothing in an existing check is loosened or removed from `all`; checks still read only --data and committed snapshots.
Host: 121 campaign tests pass, verify.py campaign and all PASS on the live data branch, lint ok.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
