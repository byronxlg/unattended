Build job (docs only): make the product runbooks true for Claude-only operation after the Codex cut on 7 Nov.
Worktree .worktrees/nz-election-runbook-fixes, branch change/nz-election-runbook-fixes from origin/main. Commit; do not push.

A read-only dry-read checked every runbook command against the tree. Fix these in product/nz_election/runbook.md and
product/nz_election/runbook/night.md (verify each claim against the cited file before writing; if the tree disagrees with
this list, the tree wins and say so in last.md):
1. night.md:138,320 say night screenshots are 1280x800; tests/night_browser.py:28, night_live_browser.py:20 use 1280x900
   (night_deployed.py:19 imports it). Distinguish the generated 1280x900 screenshots from 1280x800 acceptance evidence.
2. runbook.md:291,303,319 and night.md:188,296 counts: read the current numbers from tests/screenshots.py (routes, images),
   night_browser.py (states), night_live_browser.py (images). Better: describe where the count comes from instead of a
   number that drifts, or give the number with its source file.
3. night.md:131 claims no query defaults to the 2023 final table; pipeline/night_page.py:165 and web/night.mjs:23 make the
   default time and data dependent. Describe it; `?sequence=2023` is the explicit archive.
4. night.md:547 live path /nz-election/night/ is /unattended/nz-election/night/.
5. runbook.md:256 social fixture commands need `--now 2026-10-17T01:00:00Z` (social_page.py:79 hides the sample after 36 h).
6. runbook.md:342: the daily sunset stops scheduled collection; bin/tick's watchdog can still dispatch the daily by hand
   (sunsets.py:34 exempts workflow_dispatch).
7. night.md:515 says commit capture and manifest straight to main; product changes go through a reviewed change/* PR
   (runbook/updates.md:13). Say: merge the reviewed capture PR, then dispatch the import.

Constraints: docs only, no code or test edits; no page changes, so product/nz_election/DESIGN.md is untouched. No emojis, no em dashes.
Done: `bin/lint` prints `lint ok`; `git diff origin/main --stat` lists only the two runbook files; last.md lists each item
with the file:line you changed and the tree file:line you checked it against.
