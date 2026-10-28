# Research: what election night and the week after still lack, after #121 (read-only)

Goal: a ranked list of the last increments to build before 5 Nov (the last Codex build dispatch;
Codex ends 7 Nov 03:14Z and Claude operates alone from then).

Context: main at 6afa95d. Merged today: #118 advance publication acceptance, #119 funding totals,
#120 runbook corrections, #121 isolated Actions rehearsal of settled, official import and rollback
(workflow nz-election-night-rehearsal.yml, input import_only). The night-exercised research
(state/jobs/research-nz-election-night-exercised/last.md) listed steps never run in production:
night-live start, live poll to publish, s197 freeze blocking branch, 8 Nov stop, settlement capture,
result-import workflow, official transition, sunsets, import rollback.

Read first: state/jobs/research-nz-election-night-exercised/last.md, intent/nz-election/schedule.md,
intent/nz-election/plan-week-after.md, product/nz_election/runbook/night.md,
.github/workflows/nz-election-*.yml, product/nz_election/pipeline/sunsets.py, bin/tick (watchdogs).

Answer:
1. For each step in that list: is it now exercised in Actions (which workflow, which job, what
   proves it), exercised only by host tests (name them), or not exercised at all.
2. The ranked gaps that could break election night (7 Nov 19:00 NZDT to 8 Nov) or the official
   transition (about 27 Nov after the lab, but its code path ships now), each with the smallest
   increment that closes it: files, the proving command, why it matters, size (small/medium).
3. Anything in the runbook a Claude-only operator could not run as written (command, file:line).

Constraints: read-only; do not run network calls to production upstreams. Cite file:line for every
claim. Under 60 lines. End with the top three increments in order.
