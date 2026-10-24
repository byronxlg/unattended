Fourth fresh-context review of PR #75 (nz-election-campaign-verify), read-only. Worktree .worktrees/nz-election-campaign-verify,
branch change/nz-election-campaign-verify, head c8091e1. Diff: git diff bec0594...c8091e1 -- product. Judge against REVIEW.md.

Context: adds `verify.py campaign` (pipeline/campaign_checks.py) with named invariant checks over the campaign data
families, wired into `verify.py all`. Earlier reviews asked that no failure path put upstream text into a message.
The third review found the INPUT_ERRORS allowlist let RuntimeError/EOFError text escape, and cli() read sys.argv[1] so
option-first invocations skipped redaction. fix-3 (c8091e1) catches Exception at the campaign boundary (owned codes kept,
everything else redacted; KeyboardInterrupt/SystemExit left alone) and uses the parsed check name. Check: both paths are
closed, no failure path in campaign_checks.py or the verify.py wiring can put data, names or upstream text into a
message, log line or exit text, and non-campaign checks keep their existing behaviour; nothing in an existing check is
loosened or removed from `all`.
Host: campaign tests 181 passed; the new regressions fail on e905c50 (20 failed) and pass on c8091e1; verify.py campaign
PASS; lint ok. Do not re-run pytest (sandbox blocks the uv cache); read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
