Read-only readiness audit for the NZ election site, to choose the next build increments before Codex stops on 7 Nov 03:14Z
(last build dispatched 5 Nov). Work from main in the repo root; do not edit anything.

Read first: intent/nz-election/schedule.md (milestones 26 Oct to 14 Nov), intent/nz-election/plan-m3.md,
intent/nz-election/plan-week-after.md, intent/nz-election/pages/*.md, product/nz_election/runbook.md, runbook/, docs/codex-notes.md, state/jobs/research-nz-election-readiness-2/last.md,
evals/. Since the first audit (25 Oct 15:18Z) PRs #82 #84 #85 merged; #83 (change/nz-election-harden-gate) and #86 (change/nz-election-policy-links) are in review: treat both as landing and do not re-propose them.

For each milestone from 26 Oct (advance voting capture) to 14 Nov, say: done (with the file, test or verify command that
shows it), partly done (what is missing), or not started. Probe with read-only commands (python -c, grep, verify.py with
--data on a temp copy is fine; no network writes, no git writes). Pay special attention to: the advance-voting daily
capture from the first EC file (what code reads it, what the hand capture must look like), election-night operation
Claude-only after the cut (what in the runbook still assumes Codex), the s197 freeze, and anything a page plan ranks in
its top three questions that the live page does not yet answer.

Output: a ranked list of at most five build increments that close the largest gaps, each with goal, files, the proving
test or command, and an estimate (small/medium); then a list of supervisor-only tasks (no code). Be concrete, cite file:line.

New this round: weight the 3 Nov rehearsal steps in plan-m3.md ("Browser-access probe and rehearsal") and the 4 Nov
harden gate (every scheduled workflow green 3 days running): what would fail today if run as written. Do not repeat
readiness-2 items already merged.
