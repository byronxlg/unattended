Read-only research: which election-night and week-after steps have actually been exercised on real runs.

Context: Codex ends about 2026-11-07 03:14Z; from then Claude alone operates the NZ election site (product/nz_election/).
A dry-read already confirmed the runbook commands exist (PR #120 corrects the wording). This job asks a different question:
for each operational step from 7 Nov 18:00 NZDT to 14 Nov, has it run for real, where, and when.

Read first: product/nz_election/runbook/night.md, product/nz_election/runbook.md, runbook/ (lab), intent/nz-election/schedule.md,
intent/nz-election/plan-week-after.md, .github/workflows/ (every nz-election workflow), bin/tick, bin/night-watchdog.
Use `gh run list --workflow <file> --limit 20 --json conclusion,event,createdAt,databaseId` per workflow (read-only gh is fine).

Output, one table: step (night-live start, live poll, s197 freeze guard, stop at 8 Nov 06:00Z, result import of preliminary final,
settlement capture, official-results transition, hourly/daily/social sunsets, Pages deploy after each, rollback), the workflow or
command, last real run id and conclusion (or "never run"), whether a rehearsal covered it (name it), and the risk if it first runs on the night.
Then a ranked list of at most four gaps that a build or a rehearsal dispatch before 5 Nov could close, each with the exact
verification command. No files changed.
