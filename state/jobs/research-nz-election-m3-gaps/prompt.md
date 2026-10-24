# Research (read-only): what is left before the 30 Oct M3 night client and the 4 Nov harden milestones

Goal: a ranked, evidence-backed gap list so the supervisor can brief the next build increments
without guessing. Do not change any file.

Read first: `intent/nz-election/schedule.md` (rows Fri 30 Oct to Fri 6 Nov), `intent/nz-election/plan-m3.md`,
`intent/nz-election/pages/night.md`, `runbook/`, `.github/workflows/`, `product/nz_election/verify.py`.

For each milestone row (M3 night client, Harden, Rehearsal), answer:
1. What the row requires, item by item.
2. For each item: done / partial / missing, with the file:line or command that shows it
   (e.g. does `/night/` replay 2017, 2020 and 2023 archives, not only the demo; is the s197 freeze
   for the social daily tested; is there a rehearsal runbook section with a 60x replay procedure;
   which evals exist under `evals/` and whether each has a runnable check).
3. Run read-only commands where cheap (`uv run python product/nz_election/verify.py <check> --help`,
   `ls`, `rg`); do not run the network or the full test suite.

Output in your final message: a table (item, status, evidence) then the three increments you would
build next in order, each with files touched and the proving command. Under 80 lines.
