Fresh-context review of PR #120 (nz-election-runbook-fixes), read-only. Worktree .worktrees/nz-election-runbook-fixes,
branch change/nz-election-runbook-fixes, base origin/main. Diff: git diff origin/main...HEAD (docs only:
product/nz_election/runbook.md, product/nz_election/runbook/night.md). Judge against REVIEW.md.

Goal: the product runbooks are true for an operator who is Claude alone after 7 November: every command exists with the
flags shown, every count or size quoted matches the code, every behaviour described (sunset exemptions, watchdog, night
default sequence, image sizes, acceptance evidence) matches the file it names.
Check each changed paragraph against the code it cites (pipeline/sunsets.py, pipeline/social.py and build.py --now,
pipeline/night_page.py, web/night.mjs, tests/night_browser.py, tests/night_live_browser.py, tests/screenshots.py, bin/tick).
Flag any statement the tree contradicts, and any command that would fail as written.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
