Read-only readiness audit for the NZ election site, to choose the last build increments before Codex stops on 7 Nov 03:14Z
(last build dispatched 5 Nov). Work from main in the repo root; do not edit anything.

Read first: intent/nz-election/schedule.md (milestones 30 Oct to 14 Nov), intent/nz-election/plan-m3.md,
intent/nz-election/plan-week-after.md, intent/nz-election/pages/*.md, product/nz_election/runbook.md, runbook/,
docs/codex-notes.md, state/jobs/research-nz-election-readiness-3/last.md, evals/. Since readiness-3 (25 Oct) these merged:
#95 rehearsal contract, #96 publish rehearsal, #98 electorate design, #99 to #102 vote/, #104 night labels, #105 to #113 funding/,
#114 2026 advance count (hand-transcribed EC figures). #115 (change/nz-election-nav-legend, header nav and home legend) is
landing: do not re-propose it or readiness-3 items already merged.

For each milestone from 30 Oct (M3 night client) to 14 Nov, say: done (with the file, test or verify command that shows it),
partly done (what is missing), or not started. Probe with read-only commands (python -c, grep, verify.py with --data on a
temp copy; no network writes, no git writes). Weight: (1) the advance count from 28 Oct onward: what a supervisor must do each
day to add a day by hand (file, fields, command that proves it), and whether vote/ and home show it after the daily; (2) the
6 Nov rehearsal and 7 Nov operation Claude-only: what in runbook/ or the workflows still assumes Codex or a human step not
written down; (3) the 4 Nov harden gate (every scheduled workflow green 3 days running): what would fail today;
(4) the 8 to 14 Nov week after: specials, settled-results state, social and daily sunsets.

Output: a ranked list of at most four build increments that close the largest gaps, each with goal, files, the proving test
or command, and an estimate (small/medium); then supervisor-only tasks (no code). Be concrete, cite file:line.
