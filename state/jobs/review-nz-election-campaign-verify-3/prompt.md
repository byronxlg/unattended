Third fresh-context review of PR #75 (nz-election-campaign-verify), read-only. Worktree .worktrees/nz-election-campaign-verify,
branch change/nz-election-campaign-verify, head e905c50. Diff: git diff bec0594...e905c50 -- product. Judge against REVIEW.md.

Context: adds `verify.py campaign` (pipeline/campaign_checks.py) with named invariant checks over the campaign data
families, wired into `verify.py all`. Earlier reviews asked that no failure path put upstream text into a message.
The second review found two leaks: supplied-bundle validation (verify.py:344, :431, :494) escaped unsanitized, and an
unknown EC p_no raised a data-bearing KeyError (campaign_checks.py:94) that became a traceback. fix-2 (e905c50) guards
both boundaries with owned codes and adds marker regressions. Check: those two paths are closed and no other failure path
in campaign_checks.py or the verify.py wiring (including exceptions of any type from the parsers) can put data, names or
upstream text into a message, log line or exit text; nothing in an existing check is loosened or removed from `all`.
Host: campaign tests 157 passed; the new regressions fail on 7f027fb (23 failed) and pass on e905c50; verify.py campaign
PASS; lint ok. Do not re-run pytest (sandbox blocks the uv cache); read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
